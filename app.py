import json
import sqlite3
from collections import defaultdict

from flask import Flask, jsonify, redirect
from flasgger import Swagger

app = Flask(__name__)  # Create a Flask WSGI application
Swagger(app)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


programs_conn = sqlite3.connect('programs.db', check_same_thread=False)
programs_conn.row_factory = dict_factory

conn = sqlite3.connect('hse_data.db', check_same_thread=False)
conn.row_factory = dict_factory


@app.route('/')
def index():
    return redirect('/apidocs/#/default')


@app.route('/programs')
def programs():
    """
    Список всех программ
    ---
    responses:
      200:
        description: Список всех программ
    """
    sql = "select id, name program_name from programs"
    cursor = programs_conn.execute(sql)
    return jsonify(cursor.fetchall()), 200


@app.route('/programs/<int:program_id>')
def program(program_id):
    """
    Информация по конкретной программе
    ---
    parameters:
      - name: program_id
        in: path
        description: Идентификатор программы
        type: integer
        required: true
    responses:
      200:
        description: Информация по конкретной программе
    """
    sql = "select * from programs where id=?"
    cursor = programs_conn.execute(sql, [program_id])
    res: dict = cursor.fetchone()
    if res:
        res['openings'] = json.loads(res['openings'])
    return jsonify(res), 200


@app.route('/courses_groups')
def courses_groups():
    """
    Список специализаций и групп курсов
    ---
    responses:
      200:
        description: Список специализаций и групп курсов
    """
    return jsonify(conn.execute('select id, name, link from courses_group').fetchall()), 200


@app.route('/courses_groups/<int:group_id>')
def courses_group(group_id):
    """
    Список курсов внутри группы
    ---
    parameters:
      - name: group_id
        in: path
        description: Идентификатор группы
        type: integer
        required: true
    responses:
      200:
        description: Список курсов внутри группы
    """
    cursor = conn.execute("select id, name, link from mooc_hse where group_id=?", [group_id])
    return jsonify(cursor.fetchall()), 200


@app.route('/courses_groups/<int:group_id>/<int:course_id>')
def course(group_id, course_id):
    """
    Описание конкретного курса
    ---
    parameters:
      - name: group_id
        in: path
        description: Идентификатор группы
        type: integer
        required: true
      - name: course_id
        in: path
        description: Идентификатор курса
        type: integer
        required: true
    responses:
      200:
        description: Описание конкретного курса
    """
    cursor = conn.execute("select id, name, link, certificate, form, free, languages, subtitles"
                          " from mooc_hse where group_id=? and id=?", [group_id, course_id])
    data: dict = cursor.fetchone()
    if data:
        data['free'] = bool(data['free'])
        data['certificate'] = bool(data['certificate'])
        data['languages'] = data['languages'].split(', ')
        data['subtitles'] = data['subtitles'].split(', ')

        teachers = conn.execute("select t.*, s.id staff_id from teacher_course tc"
                                " join teachers t on tc.teacher_id = t.id"
                                " left join staff s on t.teacher_link like '%'||s.link"
                                " where tc.course_id=?", [course_id]).fetchall()
        data['teachers'] = teachers
    return jsonify(data), 200


@app.route('/staff')
def staff():
    """
    Список сотрудников ВШЭ
    ---
    responses:
      200:
        description: Список сотрудников ВШЭ
    """
    return jsonify(conn.execute('select id, link, full_name from staff').fetchall()), 200


@app.route('/staff/<int:staff_id>')
def person(staff_id):
    """
    Описание конкретного сотрудника
    ---
    parameters:
      - name: staff_id
        in: path
        description: Идентификатор сотрудника
        type: string
        required: true
    responses:
      200:
        description: Описание конкретного сотрудника
    """
    cursor = conn.execute("select id, link, full_name from staff where id=?", [staff_id])
    p: dict = cursor.fetchone()
    if p:
        data = conn.execute("select contact_type, contact_value from staff_contacts"
                            " where staff_link=?", [p['link']]).fetchall()
        contacts = defaultdict(list)
        for contact in data:
            contacts[contact['contact_type']].append(contact['contact_value'])
        p['contacts'] = contacts

        data = conn.execute("select language from staff_languages where staff_link=?", [p['link']]).fetchall()
        p['languages'] = [l['language'] for l in data]

        data = conn.execute("select i.name from staff_interests si join interests i on si.interest_id = i.id"
                            " where si.staff_link=?", [p['link']]).fetchall()
        p['interests'] = [i['name'] for i in data]

        p['adviser'] = conn.execute("select a.id, a.full_name, a.link from staff s"
                                    " join staff a on a.link=s.advisor"
                                    " where s.id=?", [staff_id]).fetchone()

    return jsonify(p), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
