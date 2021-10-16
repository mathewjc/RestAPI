from flask import Flask, request
from waitress import serve
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bugdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Bugs(db.Model):
    BugID = db.Column(db.Integer, primary_key = True)
    Title = db.Column(db.String(100), nullable = False)
    Body = db.Column(db.String(500))
    Status = db.Column(db.Integer, nullable = False)
    AssignedTo = db.Column(db.Integer)

    def __repr__(self):
        return f"{self.BugID}"

class Comments(db.Model):
    CmntID = db.Column(db.Integer, primary_key = True)
    CmntTitle = db.Column(db.String(100), nullable = False)
    CmntBody = db.Column(db.String(500))
    BugID = db.Column(db.Integer, nullable = False)
    CmntOwnr = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"{self.CmntID}"

if not os.path.isfile('./bugdata.db'):
    #create the Database
    print("creating the DB")
    db.create_all()
    db.session.commit()
else:
    print("DB already exsits")

@app.route('/', methods = ['GET'])
def index():
    return ("Welcome to BugsWorld")

@app.route('/bugs', methods = ['POST'])
def CreateBug():
    newbug = Bugs()
    #print(request.json)
    newbug.Title = request.json['Title']
    newbug.Body = request.json['Body']
    newbug.Status = 1
    newbug.AssignedTo = 0
    db.session.add(newbug)
    db.session.commit()
    return {"New Bug ID is " : newbug.BugID}

@app.route('/bugs', methods = ['GET'])
def GetBugs():
    bugs = Bugs.query.all()
    bugsJason = []
    for bug in bugs:
        comments = Comments.query.filter_by(BugID=bug.BugID)
        cmntsJason = []
        for comment in comments:
            cmntsJason.append({"CmntID": comment.CmntID, "CmntOwnr": comment.CmntOwnr, "Title": comment.CmntTitle,
                               "Body": comment.CmntBody})
        bugsJason.append({"Bugid":bug.BugID, "Title":bug.Title, "Body":bug.Body, "Status": bug.Status, "Assigned to ": bug.AssignedTo, "Comments": cmntsJason})
    return {"bugs":bugsJason}

@app.route('/bugs/<id>', methods = ['GET'])
def GetBug(id):
    bug = Bugs.query.get(id)
    if bug is None:
        return {"No bug with id:": id}
    comments = Comments.query.filter_by(BugID=id)
    cmntsJason = []
    for comment in comments:
        cmntsJason.append({"CmntID":comment.CmntID, "CmntOwnr":comment.CmntOwnr, "Title":comment.CmntTitle, "Body":comment.CmntBody})
    bugsJason = ({"Bugid":bug.BugID, "Title":bug.Title, "Body":bug.Body, "Status": bug.Status, "Assigned to ": bug.AssignedTo, "Comments": cmntsJason})
    return {"bugs":bugsJason}

@app.route('/bugs/<id>', methods = ['PUT'])
def UpdateBug(id):
    bug = Bugs.query.get(id)
    if bug is None:
        return {"No bug with id:": id}
    bug.Title = request.json['Title']
    bug.Body = request.json['Body']
    db.session.commit()
    return {"Update bug":bug.BugID}

@app.route('/bugsts/<id>', methods = ['PATCH'])
def UpdateStatus(id):
    bug = Bugs.query.get(id)
    if bug is None:
        return {"No bug with id:": id}
    bug.Status = request.json['Status']
    db.session.commit()
    return {"Status updated":bug.BugID}

@app.route('/bugasgn/<id>', methods = ['PATCH'])
def AssignBug(id):
    bug = Bugs.query.get(id)
    if bug is None:
        return {"No bug with id:": id}
    bug.AssignedTo = request.json['AssignedTo']
    db.session.commit()
    return {"Bug Assigned":bug.BugID}

@app.route('/rsbugs', methods = ['GET'])
def GetResolvedBugs():
    bugs = Bugs.query.filter_by(Status=0)
    bugsJason = []
    for bug in bugs:
        comments = Comments.query.filter_by(BugID=bug.BugID)
        cmntsJason = []
        for comment in comments:
            cmntsJason.append({"CmntID": comment.CmntID, "CmntOwnr": comment.CmntOwnr, "Title": comment.CmntTitle,
                               "Body": comment.CmntBody})
        bugsJason.append({"Bugid": bug.BugID, "Title": bug.Title, "Body": bug.Body, "Status": bug.Status,
                          "Assigned to ": bug.AssignedTo, "Comments": cmntsJason})
    return {"bugs": bugsJason}

@app.route('/bugs/<id>', methods = ['DELETE'])
def DeleteBug(id):
    bug = Bugs.query.get(id)
    if bug is None:
        return {"No bug with id:": id}
    db.session.delete(bug)
    db.session.commit()
    comments = Comments.query.filter_by(BugID=id)
    for comment in comments:
        DeleteCmnt(comment.CmntID )
    return {"Deleted Bug":id}

@app.route('/cmnts', methods = ['POST'])
def AddCmnt():
    newcmnt = Comments()
    print(request.json)
    newcmnt.CmntTitle = request.json['CmntTitle']
    newcmnt.CmntBody = request.json['CmntBody']
    newcmnt.BugID = request.json['BugID']
    newcmnt.CmntOwnr = request.json['CmntOwnr']
    db.session.add(newcmnt)
    db.session.commit()
    return {"New comment is added for ticket " : newcmnt.BugID}

@app.route('/cmnts/<id>', methods = ['DELETE'])
def DeleteCmnt(id):
    cmnt = Comments.query.get(id)
    if cmnt is None:
        return {"No comment with id:": id}
    db.session.delete(cmnt)
    db.session.commit()
    return {"Deleted Comment": id}

serve(app, host='localhost', port=5000, threads=1)
