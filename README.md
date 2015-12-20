# KamiBot

参考了Yinzo的代码: https://github.com/Yinzo/SmartQQBot

###Usage
    python main.py 
###Architecture
    1. QQ.py:   Abstract QQ's login and REST API, all received messages are saved to a queue.
    2. Dispatcher.py:  Add all addons to a pipeline, a message is passed through each addon on pipeline
    3. Addons: All the replies and logic should be handled through addon.

###API
method | Notes
--- | --- 
QR_login() | Show QR Code and login
start() | Start polling and dispatching logic  


######QQ API (basic):
method | Notes
--- | --- 
QR_login() | Show QR Code and login
start() | Start polling and dispatching logic
######QQ API (REST):
method | Notes
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
