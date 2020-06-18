from flask import Flask, request, g, render_template
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO
from flask_restful import Resource, Api
from fractalDatabase import FractalDatabase
from controller import Controller

app = Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")

app.secret_key = "secret key"
app.config['CORS_ORIGINS'] = "*"
app.config['CORS_HEADERS'] = ['Content-Type']
app.debug = True
api = Api(app)
CORS(app)

socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

def get_db():
  if "db" not in g:
    g.db = FractalDatabase("mongodb+srv://fractal-admin:nanas31110@fractal-zdnzj.gcp.mongodb.net/fractal?retryWrites=true&w=majority")

  return g.db

@app.teardown_appcontext
def teardown_db(a):
    db = g.pop("db", None)

    if db is not None:
        db.close()

#@socketio.on("broadcast_message")
#def HandleBroadcastM(data):
#    socketio.emit("post_message", data, broadcast=True)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')

class Login(Resource):
    def post(self):
        controller = Controller(get_db())
        data = request.get_json()
        result = controller.login(data["email"], data["password"])
        if(result != ""):
            return {"msg" : "success", "user" : result}

class Register(Resource):
    def post(self):
        controller = Controller(get_db())
        data = request.get_json()
        user = controller.register(data["username"], data["email"], data["password"])
        if(user is not None):
            return {"msg" : "success", "user" : user}
        else:
            return {"msg" : "fail"}

class CheckEmailSingularity(Resource):
    def get(self):
        controller = Controller(get_db())
        
        if(controller.validateEmailSingularity(request.values["email"])):
            return {"msg" : "success", "response" : "true"}

        return {"msg" : "success", "response" : "false"}

class User(Resource):
    def get(self):
        controller = Controller(get_db())

        if("user_id" in request.values):
            output = controller.getUserById(request.values["user_id"])
            if(output is not None):
                return {"msg" : "success", "user" : output}

        else:
            return {
                "msg" : "success",
                "users" : controller.getAllUsers()
            }

class FriendRequest(Resource):
    def get(self):
        controller = Controller(get_db())

        if("friend_request_id" in request.values):
            return {"msg" : "success", "friend_request" : controller.getFriendRequestById(request.values["friend_request_id"])}

        elif("recipient_id" in request.values):
            return {"msg" : "success", "friend_requests" : controller.getFriendRequestByRecipient(request.values["recipient_id"])}

        elif("sender_id" in request.values):
            return {"msg" : "success", "friend_requests" : controller.getFriendRequestBySender(request.values["sender_id"])}

        else:
            return {"msg" : "success", "friend_requests" : controller.getAllFriendRequests()}

    def post(self):
        controller = Controller(get_db())
        data = request.get_json()
        return {"msg" : "success", "friend_request" : controller.insertFriendRequest(data["sender_id"], data["recipient_id"])}

    def delete(self):
        controller = Controller(get_db())
        controller.deleteFriendRequest(request.get_json["friend_request_id"])
        return {"msg" : "success"}

class Friend(Resource):
    def get(self):
        controller = Controller(get_db())
        
        if("friend_id" in request.values):
            return {"msg" : "success", "friend" : controller.getFriendById(request.values["friend_id"])}

        elif("user_id" in request.values):
            return {"msg" : "success", "friends" : controller.getFriendsByUser(request.values["user_id"])}

        else:
            return {"msg" : "success", "friends" : controller.getAllFriends()}

    def post(self):
        controller = Controller(get_db())
        data = request.get_json()
        return {"msg" : "success", "friend" : controller.insertFriend(data["user1_id"], data["user2_id"])}

    def delete(self):
        controller = Controller(get_db())
        controller.deleteFriend(request.get_json()["friend_id"])
        return {"msg" : "success"}

class Chat(Resource):
    def get(self):
        controller = Controller(get_db())

        if("chat_id" in request.values):
            return {
                "msg" : "success",
                "chat" : controller.getChatById(request.values["chat_id"])
            }

        elif("user_id" in request.values):
            return {"msg" : "success", "chats" : controller.getChatsByUser(request.values["user_id"])}

        else:
            return {
                "msg" : "success",
                "chats" : controller.getAllChats()
            }

    def post(self):
        controller = Controller(get_db())
        data = request.get_json()
        chat = controller.createChatGroup(data["user_id"], data["chat_title"], data["chat_Pic"])

        if(chat is not None):
            return {"msg" : "success", "chat" : chat}

        return {"msg" : "fail"}
        
    def put(self):
        controller = Controller(get_db())
        data = request.get_json()
        controller.setChatGroup(data["chat_id"], data["chat_title"], data["chat_pic"])
        return {"msg" : "success"}

    def delete(self):
        controller = Controller(get_db())
        controller.deleteChat(request.get_json()["chat_id"])

        return {"msg" : "success"}
        
class Member(Resource):
    def get(self):
        controller = Controller(get_db())

        if("member_id" in request.values):
            return {"msg" : "success", "member" : controller.getMemberById(request.values["member_id"])}

        elif("chat_id" in request.values):
            members = controller.getMembersByChat(request.values["chat_id"])
        
            if members is not None:
                return {
                    "msg" : "success",
                    "members" : members
                }

            return {"msg" : "fail"}

        else:
            return{
                "msg" : "success",
                "members" : controller.getAllMembers()
            }

    def post(self):
        controller = Controller(get_db())
        data = request.get_json()
        return {"msg" : "success", "member" : controller.addMember(data["user_id"], data["chat_id"])}

    def put(self):
        controller = Controller(get_db())
        data = request.get_json()
        controller.setMember(data["member_id"], data["is_admin"], data["open"])
        return {"msg" : "success"}

    def delete(self):
        controller = Controller(get_db())
        controller.deleteMember(request.get_json()["member_id"])
        return {"msg" : "success"}

class Message(Resource):
    def get(self):
        controller = Controller(get_db())
        
        if("message_id" in request.values):
            return {
                "msg" : "success",
                "message" : controller.getMessageById(request.values["message_id"])
            }

        elif("chat_id" in request.values):
            return {
                "msg" : "success",
                "messages" : controller.getMessagesByChat(request.values["chat_id"])
            }

        else:
            return {
                "msg" : "success",
                "messages" : controller.getAllMessages()
            }

    def post(self):
        controller = Controller(get_db())
        message = controller.sendMessage(request.values["sender_id"], request.values["chat_id"], request.values["writing"], request.values["attachment"])

        if(message is not None):
            return {"msg" : "success", "message" : message}
    
        return {"msg" : "fail"}

    def put(self):
        controller = Controller(get_db())
        data = request.get_json()

        if(controller.setMessage(data["message_id"], data["writing"], data["attachment"])):
            return {"msg" : "success"}

        return {"msg" : "fail"}
        
    def delete(self):
        controller = Controller(get_db())
        controller.deleteMessage(request.get_json()["message_id"])

        return {"msg" : "success"}

class Schedule(Resource):
    def get(self):
        controller = Controller(get_db())

        if("schedule_id" in request.values):
            return {"msg" : "success", "schedule" : controller.getScheduleById(request.values["schedule_id"])}

        elif("user_id" in request.values):
            return {
                "msg" : "success",
                "schedules" : controller.getSchedulesByUser(request.values["user_id"])
            }

        else:
            return {
                "msg" : "success",
                "schedules" : controller.getAllSchedules()
            }
        
    def post(self):
        controller = Controller(get_db())
        data = request.get_json()
        schedule = controller.createSchedule(data["owner_id"], data["title"], data["type"], data["time"], data["desc"], request.values["games"])

        return {"msg" : "success", "schedule" : schedule}

    def put(self):
        controller = Controller(get_db())
        data = request.get_json()
        controller.setSchedule(data["schedule_id"], data["title"], data["type"], data["time"], data["desc"], data["games"])
        return {"msg" : "success"}

    def delete(self):
        controller = Controller(get_db())
        controller.deleteSchedule(request.get_json()["schedule_id"])
        return {"msg" : "success"}
        
class Participant(Resource):
    def get(self):
        controller = Controller(get_db())

        if("participant_id" in request.values):
            return {
                "msg" : "success",
                "participant" : controller.getParticipantById(request.values["participant_id"])
            }

        elif("schedule_id" in request.values):
            return {
                "msg" : "success",
                "participants" : controller.getParticipantsBySchedule(request.values["schedule_id"])
            }

        else:
            return {
                "msg" : "success",
                "participants" : controller.getAllParticipants()
            }    
        
    def post(self):
        controller = Controller(get_db())
        data = request.get_json()

        return {"msg" : "success", "participant" : controller.addParticipant(data["user_id"], data["schedule_id"])}

    def put(self):
        controller = Controller(get_db())
        controller.setParticipant(request.values["participant_id"], request.values["accepted"])
        return {
            "msg" : "success"
        }

    def delete(self):
        controller = Controller(get_db())
        controller.deleteParticipant(request.get_json()["participant_id"])
        return {"msg" : "success"}

api.add_resource(Login, "/api/login")
api.add_resource(Register, "/api/register")
api.add_resource(CheckEmailSingularity, "/api/check_email_singularity")
api.add_resource(User, "/api/user")
api.add_resource(FriendRequest, "/api/friend_request")
api.add_resource(Friend, "/api/friend")
api.add_resource(Chat, "/api/chat")
api.add_resource(Member, "/api/member")
api.add_resource(Message, "/api/message")
api.add_resource(Schedule, "/api/schedule")
api.add_resource(Participant, "/api/participant")

if __name__ == '__main__':
    socketio.run(app)
