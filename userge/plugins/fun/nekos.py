import nekos
from userge import userge, Message
from userge.utils import rand_array


NSFW = ['feet', 'yuri', 'trap', 'futanari', 'hololewd', 'lewdkemo', 'holoero',
        'solog', 'feetg', 'cum', 'erokemo', 'les', 'lewdk', 'lewd','eroyuri', 'eron',
        'cum_jpg', 'bj', 'nsfw_neko_gif', 'solo', 'kemonomimi', 'nsfw_avatar',
        'gasm', 'anal', 'hentai','erofeet', 'keta', 'blowjob', 'pussy', 'tits',
        'pussy_jpg', 'pwankg', 'classic', 'kuni', 'femdom', 'spank', 'erok', 'boobs', 
        'random_hentai_gif', 'smallboobs','ero', 'smug']

NON_NSFW = ['baka', 'smug', 'hug', 'fox_girl', 'cuddle', 'neko',
            'pat', 'waifu', 'kiss', 'holo', 'avatar', 'slap', 'gecg', 
            'feed', 'tickle', 'ngif', 'wallpaper', 'poke']


neko_help = """
<b>NSFW</b>:  <code>feet  yuri  trap  futanari  hololewd  lewdkemo  holoero  solog  feetg
cum  erokemo  les  lewdk  lewd  eroyuri  eron  cum_jpg  bj  nsfw_neko_gif  
solo  kemonomimi  nsfw_avatar  gasm  anal  hentai  erofeet  keta  blowjob  
pussy  tits  pussy_jpg  pwankg  classic  kuni  femdom  spank  erok  boobs  
random_hentai_gif  smallboobs  ero  smug</code>

<b>SFW</b>:  <code>baka  smug  hug  fox_girl  cuddle  neko  pat  waifu  kiss
holo  avatar  slap  gecg  feed  tickle  ngif  wallpaper  poke</code>
"""


@userge.on_cmd("nekos", about={
    'header': "Get NSFW / SFW stuff from nekos.life",
    'flags': {"nsfw": "For random NSFW"},
    'usage': "{tr}nekos\n{tr}nekos -nsfw\n{tr}nekos [Choice]",
    'Choice': neko_help})
async def neko_life(message: Message):
    choice = message.input_str
    if '-nsfw' in message.flags:
        choosen_ = rand_array(NSFW)
    elif choice:
        neko_all = NON_NSFW + NSFW
        choosen_ = (choice.split())[0]
        if choosen_ not in neko_all:
            await message.err('Choose a valid Input !, See Help for more info.', del_in=5)
            return
    else:
        choosen_ = rand_array(NON_NSFW)
    link = nekos.img(choosen_)
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else None
    if link.endswith('.gif'):
        await message.client.send_animation(
            chat_id=message.chat.id,
            animation=link,
            unsave=True,
            reply_to_message_id=reply_id
        )
    else:
        await message.client.send_photo(
            chat_id=message.chat.id,
            photo=link,
            reply_to_message_id=reply_id
        )
    await message.delete()