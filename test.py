# import json
#
# users_info = {
#    "users_amount": 1,
#    "users": {
#       "\u041a\u0432\u0430\u043a\u0448\u0430#5955": {
#          "money": {
#             "usd": 10000.0
#          },
#          "settings": {
#             "ingame": True,
#             "comissiondiff": 1,
#             "moneydiff": 2,
#             "comission": 0.001,
#             "comission_factor": 0.999
#          }
#       }
#    },
#    "bot_settings": {
#       "showing_settings": {
#          "comissiondiff": "Сложность по комиссии",
#          "moneydiff": "Сложность по деньгам",
#          "comission": "Комиссия"
#       }
#    }
# }
#
# with open('test.json', 'w') as file:
#     json.dump(users_info, file, indent=3)
a = (1, 2, 3, 4)
b, c, d = a
print(c)