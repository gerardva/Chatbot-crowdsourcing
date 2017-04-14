from decimal import Decimal

from api.code.model import *

REWARD = '0.05'


def add_api_routes(app):
    app.add_route('/worker/{user_id}/tasks', WorkerTasksResource())
    app.add_route('/worker/{user_id}/answers', WorkerAnswersResource())
    app.add_route('/worker', WorkerResource())
    app.add_route('/worker/{user_id}', WorkerUserIdResource())
    app.add_route('/requester/questions/{question_id}', RequesterQuestionResource())
    app.add_route('/requester/tasks', RequesterTasksResource())
    app.add_route('/requester/tasks/{task_id}/answers', RequesterTasksAnswersResource())

mysql_db.create_tables([User, Task, Question, Content, Answer, Location, CanNotAnswer], safe=True)


class WorkerAnswersResource:
    def on_post(self, req, resp, user_id):
        last_answer = req.get_param_as_bool("last")

        req_as_json = json.loads(req.stream.read().decode('utf-8'))

        answer = Answer.create(answer=req_as_json['answer'],
                               user=user_id,
                               content=req_as_json['contentId'],
                               question=req_as_json['questionId'])

        answer.save()
        response = {
            'success': True
        }
        if last_answer:
            query = User.update(score=User.score + Decimal(REWARD)).where(User.id == user_id)
            query.execute()
            response['reward'] = REWARD
        resp.body = json.dumps(response)


class WorkerTasksResource:
    def on_get(self, req, resp, user_id):
        contents = self.build_get_tasks_query(req, user_id)

        tasks = []
        for content in contents:
            questions = content.task.questions.order_by(Question.index)

            questions_json = []
            for question in questions:
                questions_json.append({
                    'questionId': question.id,
                    'index': question.index,
                    'question': question.question,
                    'answerSpecification': question.answerSpecificationJSON
                })

            task = content.task

            task_data = {
                'taskId': task.id,
                'description': task.description,
                'contentId': content.id,
                'content': content.dataJSON,
                'questions': questions_json
            }

            try:
                location = content.location.get()
                task_data['location'] = {
                    'latitude': location.latitude,
                    'longitude': location.longitude
                }
            except DoesNotExist:
                # if no location is present, that is fine
                pass

            tasks.append(task_data)
        resp.body = json.dumps(tasks)

    @staticmethod
    def build_get_tasks_query(req, user_id):
        # read parameters
        limit = req.get_param("limit")
        order = req.get_param("order", default="random")

        # start building subquery
        # the subquery returns a single content id per task, for all contents
        # that match the worker's query and the worker is allowed to do
        subquery = None
        if order == "random":
            subquery = Content.select(fn.Min(Content.id))
        elif order == "location":
            subquery = WorkerTasksResource.build_location_subquery(req)

        # filter out contents that this worker can not answer
        # (e.g. due to having answered the original task that this is a review task of)
        subquery = subquery.join(CanNotAnswer, JOIN.LEFT_OUTER, on=(Content.id == CanNotAnswer.content)).where(
            (CanNotAnswer.user.is_null()) | (CanNotAnswer.user != user_id))

        # filter out contents that this user has already answered
        subquery = subquery.join(Answer, JOIN.LEFT_OUTER, on=(Content.id == Answer.content)).where(
            (Answer.user.is_null()) | (Answer.user != user_id))

        # group by task, meaning the minimum content id per task is returned
        subquery = subquery.group_by(Content.task)

        # get a content for each task
        # we join it with Task to prevent N+1 queries to get the associated task later
        contents = Content.select(Content, Task).join(Task).where(Content.id << subquery).order_by(fn.Rand())

        if limit:
            try:
                limit_int = int(limit)
                contents = contents.limit(limit_int)
            except ValueError:
                # ignore limit parameter if it is not an integer
                pass
        return contents

    @staticmethod
    def build_location_subquery(req):
        # does not use circle dist, but square with sides of 2 x maxDist
        max_dist = float(req.get_param("range"))
        longitude = float(req.get_param("longitude"))
        latitude = float(req.get_param("latitude"))

        max_longitude = longitude + max_dist
        min_longitude = longitude - max_dist
        max_latitude = latitude + max_dist
        min_latitude = latitude - max_dist
        # get location within square of sides r with long and lat as center, randomize these points
        # (for limiting alter on for example)
        return Content.select(fn.Min(Content.id)).join(Location).where(
            (Location.longitude >= min_longitude) &
            (Location.longitude <= max_longitude) &
            (Location.latitude >= min_latitude) &
            (Location.latitude <= max_latitude))


class WorkerResource:
    def on_post(self, req, resp):
        req_as_json = json.loads(req.stream.read().decode('utf-8'))
        facebook_id = req_as_json['facebookId']

        if facebook_id:
            try:
                user = User.select().where(User.facebookId == facebook_id).get()
            except DoesNotExist:
                new_user = User.create(facebookId=facebook_id)
                new_user.save()
                user = User.select().where(User.facebookId == facebook_id).get()

            resp.body = json.dumps({'userId': user.id})
        else:
            resp.body = json.dumps({'error': 'No Facebook ID provided. '
                                             'Other platforms are not supported at this time.'})


class WorkerUserIdResource(object):
    def on_get(self, req, resp, user_id):
        user = User.get(User.id == user_id)
        response = {
            'facebookId': user.facebookId,
            'score': str(user.score)
        }
        resp.body = json.dumps(response)


class RequesterTasksResource:
    def on_get(self, req, resp):
        task_id = req.get_param('taskId')
        try:
            task = Task.select().where(Task.id == task_id).get()
            resp.body = json.dumps(task.as_json())
        except DoesNotExist:
            resp.body = {}

    def on_post(self, req, resp):
        request_dict = json.loads(req.stream.read().decode('utf-8'))
        task = Task.create(user=request_dict['userId'],
                           description=request_dict['description'])
        task.save()

        for index, question_json in enumerate(request_dict['questionRows']):
            question_string = question_json['question']
            answer_specification = question_json['answerSpecification']
            new_question = Question.create(index=index,
                                           question=question_string,
                                           answerSpecificationJSON=json.dumps(answer_specification),
                                           task=task.id)

        i = 0
        for content in request_dict['content']:
            content_id = None
            if 'data' in content:
                content_id = Content.create(dataJSON=json.dumps(content['data']), task=task.id)
            else:
                content_id = Content.create(task=task.id)
            if 'location' in content:
                add_location(content_id, content['location'])

            # todo we should probably make canNotMake available at the content level,
            # but i did not want to break things. (this would removal of the i)
            if 'canNotMake' in request_dict:
                can_not_be_made_by_users = request_dict['canNotMake'][i]
                for userId in can_not_be_made_by_users:
                    can_not_make_id = CanNotAnswer.create(user=userId, content=content_id)
            i += 1

        resp.body = json.dumps({'taskId': task.id})


def add_location(content_id, location_as_json):
    location = Location.create(content=content_id,
                               latitude=location_as_json['latitude'],
                               longitude=location_as_json['longitude'])
    location.save()


class RequesterQuestionResource:
    def on_get(self, req, resp, question_id):
        question = Question.get(Question.id == question_id)
        resp.body = json.dumps(question.as_json())


class RequesterTasksAnswersResource:
    def on_get(self, req, resp, task_id):
        # if we want to return the actual objects, in addition to their ids
        elaborate = req.get_param_as_bool('elaborate')

        task_id_int = int(task_id)

        print(task_id_int)
        answers = Answer.select(Answer, Content, User, Task) \
            .join(Content) \
            .join(Task) \
            .join(User) \
            .where(Task.id == task_id_int)

        answers_list = []
        for answer in answers:
            result_answer = {
                'answer': answer.answer,
                'contentId': answer.content.id,
                'questionId': answer.question.id,
                'userId': answer.user.id,
                'taskId': answer.content.task.id
            }
            if elaborate:
                result_answer['content'] = answer.content.as_json()
                result_answer['user'] = answer.user.as_json()
                result_answer['question'] = answer.question.as_json()
                result_answer['task'] = answer.content.task.as_json()

            answers_list.append(result_answer)

        resp.body = json.dumps(answers_list)
