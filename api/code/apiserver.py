import json

from api.code.apifuncs.api import QuoteResource
from api.code.model import *

REWARD = 0.05

def add_api_routes(app):
    app.add_route('/quote', QuoteResource())
    app.add_route('/worker/tasks', WorkerTasksResource())
    app.add_route('/worker/{user_id}/answers', WorkerAnswersResource())
    app.add_route('/worker/users', WorkerUsersResource())
    app.add_route('/worker/{user_id}', WorkerResource())
    app.add_route('/requester/tasks', RequesterTasksResource())
    app.add_route('/requester/tasks/{task_id}/answers', RequesterTasksAnswersResource())

mysql_db.create_tables([User, Task, Question, Content, Answer, Location], safe=True)


class WorkerAnswersResource:
    def on_post(self, req, resp, user_id):
        last_answer = req.get_param("last") == "true"
        req_as_json = json.loads(req.stream.read().decode('utf-8'))

        answer = Answer.create(answer=req_as_json['answer'],
                               userId=req_as_json['userId'],
                               contentId=req_as_json['contentId'],
                               questionId=req_as_json['questionId'])

        answer.save()
        response = {
            'success': True
        }
        if last_answer:
            query = User.update(score=User.score + REWARD).where(User.id == user_id)
            query.execute()
            response['reward'] = REWARD
        resp.body = json.dumps(response)


class WorkerTasksResource:
    def on_get(self, req, resp):
        # read parameters
        limit = req.get_param("limit")
        order = req.get_param("order")
        # start building query
        contents = None
        if order == "random":
            contents = Content.select().order_by(fn.Rand())
        elif order == "location":
            # does not use circle dist, but square with sides of 2 x maxDist
            max_dist = float(req.get_param("range"))
            longitude = float(req.get_param("longitude"))
            latitude = float(req.get_param("latitude"))

            maxLongitude = longitude + max_dist
            minLongitude = longitude - max_dist
            maxLatitude = latitude + max_dist
            minLatitude = latitude - max_dist
            # get location within square of sides r with long and lat as center, randomize these points
            # (for limiting alter on for example)
            contents = Content.select(Content, Location).join(Location).where(
                (Location.longitude >= minLongitude) &
                (Location.longitude <= maxLongitude) &
                (Location.latitude >= minLatitude) &
                (Location.latitude <= maxLatitude)).order_by(fn.rand())

        if contents is None:
            # when no contents exist, nothing can be returned
            resp.body = {}
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
                print('no location found, so not adding to content for contentId ' + str(content.id))

            tasks.append(task_data)
        resp.body = json.dumps(tasks)


class WorkerUsersResource:
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


class WorkerResource(object):
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
            new_question.save()

        for content in request_dict['content']:
            if 'data' in content:
                content_id = Content.create(dataJSON=json.dumps(content['data']), taskId=task.id)
            else:
                content_id = Content.create(taskId=task.id)
            if 'location' in content:
                add_location(content_id, content['location'])

        resp.body = json.dumps({'taskId': task.id})


def add_location(content_id, location_as_json):
    location = Location.create(contentId=content_id,
                               latitude=location_as_json['latitude'],
                               longitude=location_as_json['longitude'])
    location.save()


class RequesterTasksAnswersResource:
    def on_get(self, req, resp, task_id):
        try:
            task_id_int = int(task_id)

            # todo: get all answers grouped by content they relate to
            print(task_id_int)
            answers = Answer.select(Answer, Content, Task).join(Content).join(Task).where(Task.id == task_id_int)

            answers_list = []
            for answer in answers:
                answers_list.append({
                    'answer': answer.answer,
                    'contentId': answer.contentId.id,
                    'taskId': answer.contentId.taskId.id
                })
            resp.body = json.dumps(answers_list)
        except ValueError:
            pass
