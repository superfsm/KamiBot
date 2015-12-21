# KamiBot

参考了Yinzo的代码: https://github.com/Yinzo/SmartQQBot

###Usage
    python main.py 
###Architecture
    1. QQ.py:   On a dedicated thread, push all received message to a queue. Abstract of QQ REST API.
    2. Dispatcher.py:  On a dedicated thread, deque a message and passed it through the pipeline, of addons
    3. Addons: All addons form the pipeline. Each addon can choose to consume the message or not.
               Can add/remove/modify addons without restart the program through superuser command.
###Setup
######Config.py
    addons: A lsit of string, indicating the addons under "addons" folder that you want to enable
    group_su: superuser's QQ number, where you can execute superuser command
    name_su: superuser's command handler's name
######Superuser Command:
    ##!ping: ping if the system is online
    ##!list: list all the addons loaded
    ##!reload: reload all addons (after you modify the codes of addons or Config)
###API
######class Message:

    message type:
    0: personal message
    1: group message
    2: discussion message

method | Notes
--- | --- 
send() | reply self.reply_txt to where it comes from
send_txt(txt) | reply txt to where it comes from
send_txt_to_type(type, uin, txt) | reply txt of certain type to a uin


######class QQ:
method | Notes
--- | --- 
QR_login() | Show QR Code and login
start() | Start polling and dispatching logic
--- | --- 
get_friend_uin(tuin) | uin->QQ号
get_self_info() |
get_user_friends() | get all friends
get_group_name_list_mask() | get all groups
get_discus_list() | get all discussions
get_online_buddies() |
get_discu_info(did) |
get_recent_list() |
change_status('away') | ['online','away','callme','busy','silent','hidden','offline']
get_friend_info(tuin) |
get_single_long_nick(tuin) | 显示目标签名
get_group_info_ext(gcode) | 

