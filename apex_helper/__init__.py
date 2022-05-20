# 所有机器人指令
from .utils import *
from .Enum import CmdEnum, UsageEnum
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Event


helper_matcher = on_command(CmdEnum.HELP.value)
@helper_matcher.handle()
async def _():
    helper_info = ""
    attr = [a for a in dir(UsageEnum) if not a.startswith('__')]
    for a in attr:
        helper_info +=  getattr(UsageEnum, a).value + '\n'
    helper_info = helper_info.lstrip('\n') 
    helper_info = helper_info.rstrip('\n')
    await helper_matcher.send(helper_info)

bind_matcher = on_command(CmdEnum.BIND.value)
@bind_matcher.handle()
async def _(event: Event, text: Message = CommandArg()):
    args = Utils.get_args(text)

    if len(args) < 1:
        await bind_matcher.send('请输入EA ID!')
        return 

    EA_ID = args[0]
    response = Query.record(EA_ID)
    if response.status_code != 200:
        print(response.content.decode("utf-8"))
        await bind_matcher.send('EA ID疑似有误!')
    else:
        QQ_EA = Persistence.load()
        QQ = event.get_user_id()
        QQ_EA[QQ] = EA_ID
        Persistence.write(QQ_EA)
        await bind_matcher.send('成功将{QQ_ID}与{EA_ID}绑定！'.format(QQ_ID=QQ, EA_ID=EA_ID))

map_matcher = on_command(CmdEnum.MAP.value)
@map_matcher.handle()
async def _():
    response = Query.map()
    if response.status_code != 200:
        await map_matcher.send('apex查询地图功能出错!')
        return 
    content = eval(response.content.decode("utf-8"))
    brs = content['battle_royale']
    ranks = content['ranked']


    current_rand_br = Utils.try_translate_br(brs['current']['map'])
    next_rand_br = Utils.try_translate_br(brs['next']['map'])
    trans_min = brs['current']['remainingMins']
    
    current_rank_br = Utils.try_translate_br(ranks['current']['map'])
    next_rank_br =  Utils.try_translate_br(ranks['next']['map'])
    trans_day = ranks['current']['remainingMins']//60//24
    
    map_info = \
"""
[匹配]: 
  当前地图: {current_rand_br}
  下一地图: {next_rand_br}
  轮换时间: {trans_min}min后
[排位]: 
  当前地图: {current_rank_br}
  下一地图: {next_rank_br}
  轮换时间: {trans_day}天后
""".format( current_rand_br=current_rand_br, next_rand_br=next_rand_br, trans_min=trans_min,\
            current_rank_br=current_rank_br, next_rank_br=next_rank_br, trans_day=trans_day)

    map_info = map_info.lstrip('\n') 
    map_info = map_info.rstrip('\n')

    await map_matcher.send(map_info)

playerInfo_matcher = on_command(CmdEnum.RECORD.value)
@playerInfo_matcher.handle()
async def _(event: Event, text: Message = CommandArg()):

    args = Utils.get_args(text)
    response = None
    if len(args) > 1:
        await playerInfo_matcher.send(UsageEnum.RECORD.value)
        return
    elif len(args) == 1:
        response = Query.record(args[0])
        if response.status_code != 200:
            await playerInfo_matcher.send('EA ID疑似有误!')
            return
    else:
        QQ = event.get_user_id()
        QQ_EA = Persistence.load()
        if QQ_EA.get(QQ) is None:
            await playerInfo_matcher.send('{QQ}未绑定EA ID!'.format(QQ=QQ))
            return
        response = Query.record(QQ_EA[QQ])
        if response.status_code != 200:
            await playerInfo_matcher.send('绑定的EA ID疑似有误!')
            return

    p = PlayerInfo(response.json())
    rankscore, rankname, rankdiv = p.rank()
    
    playerInfo = \
"""
[等级]: {level}
[本赛季排位]: 
    分数: {rank_score}
    段位: {rank_name} {rank_div}
""".format(level=p.level(), rank_score=rankscore, rank_name=rankname, rank_div = rankdiv)
    playerInfo=playerInfo.rstrip('\n')
    playerInfo=playerInfo.lstrip('\n')
    await playerInfo_matcher.send(playerInfo)
            

crafting_matcher = on_command(CmdEnum.CRAFTING.value)
@crafting_matcher.handle()
async def _():
    response = Query.crafting()

    if response.status_code != 200:
        await map_matcher.send('apex查询制造功能出错!')
        return 
    crafting = []
    for j in range(2):
        crafting_js = response.json()[j]['bundleContent']
        for i in range(2):
            crafting.append(crafting_js[i]['itemType']['name'])
        
    crafting_info = \
'''
[今日制造]: {daily_craftint1}, {daily_craftint2}
[本周制造]: {weekly_crafting1}, {weekly_crafting2}
'''.format( daily_craftint1=Utils.try_translate_crafting(crafting[0]), 
            daily_craftint2=Utils.try_translate_crafting(crafting[1]), 
            weekly_crafting1=Utils.try_translate_crafting(crafting[2]), 
            weekly_crafting2=Utils.try_translate_crafting(crafting[3])
            )
    crafting_info=crafting_info.rstrip('\n')
    crafting_info=crafting_info.lstrip('\n')
    await crafting_matcher.send(crafting_info)
        