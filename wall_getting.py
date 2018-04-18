import vk_api
import sqlite3
import time

def main(token):
    token = token
    vk_session = vk_api.VkApi(
                               app_id=6443431,
                            token=token,
                            api_version='5.74',
                            scope=8194
                              )
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
    vk = vk_session.get_api()
    return vk


def wall_get(tg_id):

    print(tg_id)
    super_box = []
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    token = c.execute('SELECT token FROM users WHERE tg_id=?', (tg_id,))
    vk = main(token.fetchone())
    c.execute('DELETE FROM groups_vk')
    start_time = c.execute('SELECT start_time FROM users WHERE tg_id=?', (tg_id,))
    response = vk.newsfeed.get(max_photos=2, count=10, start_time=start_time.fetchone())
    start_time = int(time.time())
    c.execute('UPDATE users SET start_time=? WHERE tg_id=?', (start_time, tg_id,))
    conn.commit()

    info = response['groups']

    for x in info:
        id_name = (x['name'], x['id'])
        c.execute('INSERT INTO groups_vk VALUES (?,?)', id_name)
    conn.commit()
    info = response['items']
    for x in response['profiles']:
        name = x['first_name'] +' '+ x['last_name']
        id_name = (name, x['id'])
        c.execute('INSERT INTO groups_vk VALUES (?,?)', id_name)


    for post in info:
        box = {'info': [0, 0, 0], 'group_name':'', 'content': {'text': [], 'photo': []}}  # 0 - text, 1- photo, 2 - id
        box['info'][2] = post['source_id']
        if  box['info'][2] < 0:
            box['info'][2] = box['info'][2] *(-1)
        if 'text' in post.keys() and len(post['text']) != 0:
            box['info'][0] += 1
            box['content']['text'].append(post['text'])
        if 'attachments' in post.keys():
            x = (post['attachments'])
            for elements in x:
                if 'photo' in elements:
                    y = elements['photo']
                    box['info'][1] += 1
                    box['content']['photo'].append(y['photo_604'])
        if box not in super_box:
            if box['info'][0] != 0 or box['info'][1] != 0:
                c.execute('SELECT group_name FROM groups_vk WHERE id_from_group=?',(box['info'][2],))
                group_name = c.fetchone()
                box['group_name'] = group_name
                super_box.append(box)
    conn.commit()
    conn.close()
    x = True
    if x == True:
        return super_box


def registration(token,tg_id):
    token = token
    vk = main(token)
    tg_id = tg_id
    info = vk.account.getProfileInfo()
    first_name =info['first_name']
    last_name = info['last_name']
    city = info['city']['title']
    phone = info['phone']
    start_time  = int(time.time())

    all_info = (first_name, last_name, tg_id, city, phone, token, start_time, )
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?)', (all_info), )
    conn.commit()
    conn.close()

