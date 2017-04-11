from decimal import Decimal

from api.code.apifuncs.api import QuoteResource
from api.code.model import *

REWARD = '0.05'

def add_api_routes(app):
    app.add_route('/quote', QuoteResource())
    app.add_route('/worker/{user_id}/tasks', WorkerTasksResource())
    app.add_route('/worker/{user_id}/answers', WorkerAnswersResource())
    app.add_route('/worker', WorkerResource())
    app.add_route('/worker/{user_id}', WorkerUserIdResource())
    app.add_route('/requester/tasks', RequesterTasksResource())
    app.add_route('/requester/tasks/{task_id}/answers', RequesterTasksAnswersResource())

mysql_db.create_tables([User, Task, Question, Content, Answer, Location, CanNotAnswer], safe=True)


class WorkerAnswersResource:
    def on_post(self, req, resp, user_id):
        last_answer = req.get_param_as_bool("last")

        req_as_json = json.loads(req.stream.read().decode('utf-8'))

        answer = Answer.create(answer=req_as_json['answer'],
                               userId=user_id,
                               contentId=req_as_json['contentId'],
                               questionId=req_as_json['questionId'])

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
        # read parameters
        limit = req.get_param("limit")
        order = req.get_param("order")

        # start building query
        contents = None
        if order == "random":
            contents = Content.select()
        elif order == "location":
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
            contents = Content.select(Content, Location).group_by(Content.taskId).join(Location).where(
                (Location.longitude >= min_longitude) &
                (Location.longitude <= max_longitude) &
                (Location.latitude >= min_latitude) &
                (Location.latitude <= max_latitude))

        # each of these filters may make contents none, so repeated checks are needed
        if contents is not None:
            contents = contents.join(CanNotAnswer, JOIN.LEFT_OUTER, on=(Content.id == CanNotAnswer.contentId)).where(
                (CanNotAnswer.userId.is_null()) | (CanNotAnswer.userId != user_id))

        if contents is not None:
            contents = contents.join(Answer, JOIN.LEFT_OUTER, on=(Content.id == Answer.contentId)).where(
                (Answer.userId.is_null()) | (Answer.userId != user_id))

        if contents is not None:
            contents = contents.group_by(Content.taskId).order_by(fn.rand())

        if contents is None or len(contents) == 0:
            # when no contents exist, nothing can be returned
            resp.body = json.dumps({})
            return

        if limit:
            try:
                limit_int = int(limit)
                contents = contents.limit(limit_int)
            except ValueError:
                # ignore limit parameter if it is not an integer
                pass

        tasks = []
        # TODO: query by task, so user can get a list of different tasks to choose from instead of different contents
        for content in contents:
            questions = Question.select(Question, Task).join(Task).where(Task.id == content.taskId).order_by(Question.index)

            questions_json = []
            for question in questions:
                questions_json.append({
                    'questionId': question.id,
                    'index': question.index,
                    'question': question.question,
                    'answerSpecification': question.answerSpecificationJSON
                })

            task = content.taskId

            task_data = {
                'taskId': task.id,
                'description': task.description,
                'contentId': content.id,
                'content': content.dataJSON,
                'questions': questions_json
            }

            try:
                # TODO: i believe kilian already made the relation 1 to 0..1, so then the .first() might be redundant.
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
            resp.body = json.dumps({'error': 'no facebook id is provided, other platforms are not supported at this time.'})


class WorkerUserIdResource(object):
    def on_get(self, req, resp, user_id):
        user = User.get(User.id == user_id)
        response = {
            'facebookId': user.facebookId,
            'score': user.score
        }
        resp.body = json.dumps(response)


    # def on_get(self, req, resp):
    #     user = User.create()
    #     resp.body = json.dumps({'userId': user.id})


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
        task = Task.create(userId=request_dict['userId'],
                           description=request_dict['description'])
        task.save()

        for index, question_json in enumerate(request_dict['questionRows']):
            question_string = question_json['question']
            answer_specification = question_json['answerSpecification']
            new_question = Question.create(index=index,
                                           question=question_string,
                                           answerSpecificationJSON=json.dumps(answer_specification),
                                           taskId=task.id)

        i = 0
        for content in request_dict['content']:
            content_id = None
            if 'data' in content:
                content_id = Content.create(dataJSON=json.dumps(content['data']), taskId=task.id)
            else:
                content_id = Content.create(taskId=task.id)
            if 'location' in content:
                add_location(content_id, content['location'])

            # todo we should probably make canNotMake available at the content level,
            # but i did not want to break things. (this would removal of the i)
            if 'canNotMake' in request_dict:
                can_not_be_made_by_users = request_dict['canNotMake'][i]
                for userId in can_not_be_made_by_users:
                    can_not_make_id = CanNotAnswer.create(userId=userId, contentId=content_id)
            i += 1

        resp.body = json.dumps({'taskId': task.id})


def add_location(content_id, location_as_json):
    location = Location.create(contentId=content_id,
                               latitude=location_as_json['latitude'],
                               longitude=location_as_json['longitude'])
    location.save()


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
                'contentId': answer.contentId.id,
                'questionId': answer.questionId.id,
                'userId': answer.userId.id,
                'taskId': answer.contentId.taskId.id
            }
            if elaborate:
                result_answer['content'] = answer.contentId.as_json()
                result_answer['user'] = answer.userId.as_json()
                result_answer['question'] = answer.questionId.as_json()
                result_answer['task'] = answer.contentId.taskId.as_json()

            answers_list.append(result_answer)

        resp.body = json.dumps(answers_list)
