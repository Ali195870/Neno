import random
import time
import requests
from highrise import BaseBot, Highrise, Position, AnchorPosition, Reaction
from highrise import __main__
from asyncio import run as arun
from emotes import Dance_Floor
import asyncio
from random import choice
import json
from typing import List
from datetime import datetime, timedelta
from highrise.models import SessionMetadata
import re
from highrise.models import SessionMetadata,  GetMessagesRequest, User ,Item, Position, CurrencyItem, Reaction
from typing import Any, Dict, Union
from highrise.__main__ import *
import asyncio, random
from emotes import Emotes
owners = ['alionardo_','devil_808']

class BotDefinition:
    
      
    def __init__(self, bot, room_id, api_token):
        self.bot = bot
        self.room_id = room_id
        self.api_token = api_token
        self.following_username = None

class Counter:
    bot_id = ""
    static_ctr = 0
    usernames = ['Alionardo_']

class Bot(BaseBot):
    continuous_emote_tasks: Dict[int, asyncio.Task[Any]] = {}  
    user_data: Dict[int, Dict[str, Any]] = {}
    continuous_emote_task = None
    cooldowns = {}  # Class-level variable to store cooldown timestamps
    emote_looping = False
    
    def __init__(self):
        super().__init__()
        self.load_membership()
        self.load_moderators()
        self.load_temporary_vips()
        self.following_username = None
        self.maze_players = {}
        self.user_points = {}  # Dictionary to store user points
        self.Emotes = Emotes
        self.should_stop = False
        self.announce_task = None
        self.convo_id_registry = []
 
      
    def load_temporary_vips(self):
        try:
            with open("temporary.json", "r") as file:
                self.temporary_vips = json.load(file)
        except FileNotFoundError:
            self.temporary_vips = {}
   
    def save_temporary_vips(self):
      with open("temporary.json", "w") as file:
          json.dump(self.temporary_vips, file)
    def load_moderators(self):
        try:
            with open("moderators.json", "r") as file:
                self.moderators = json.load(file)
        except FileNotFoundError:
            self.moderators = []

        # Add default moderators here
        default_moderators = ['Alionardo_']
        for mod in default_moderators:
            if mod.lower() not in self.moderators:
                self.moderators.append(mod.lower())
       
    def load_membership(self):
     try:
        with open("membership.json", "r") as file:
            self.membership = json.load(file)
     except FileNotFoundError:
        self.membership = []
    def save_membership(self):
     with open("membership.json", "w") as file:
        json.dump(self.membership, file)

  
    def save_moderators(self):

      with open("moderators.json", "w") as file:
            json.dump(self.moderators, file)

  
    async def announce(self,user_input,message: str):
      while True:  
              await asyncio.sleep(6)
              await self.highrise.chat(user_input)
              await asyncio.sleep(60)
              await self.highrise.send_emote('emote-hello')
  
    async def on_start(self, session_metadata: SessionMetadata) -> None:
      try:
       
        Counter.bot_id = session_metadata.user_id
        print("Ali is booting ...")

        await self.highrise.walk_to(Position(1.5, 6.25,1.5, facing='FrontRight'))
        self.load_temporary_vips()
        await asyncio.sleep(6)
        await self.highrise.chat(f"Deployed ")
      except Exception as e:
          print(f"An exception occured: {e}")  
    async def on_emote(self, user: User ,emote_id : str , receiver: User | None )-> None:
      print (f"{user.username} , {emote_id}")

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:

     try:

        await self.highrise.send_whisper(user.id,f"\n ____________________________\nHello {user.username}\nWelcome to PRH 🐰 DJDEV 💜 TIPS \n• Message or dm or Whisper !list or -list \nto veiw the functions.\n ____________________________\nbot made by @Alionardo_")
        await self.highrise.send_emote('emote-salute')
     
     except Exception as e:
            print(f"An error on user_on_join: {e}") 


    async def on_user_next_leave(self, user: User, message: str ) -> None:
      try:
        print(f"{user.username} has left the room")
        await self.highrise.chat(f"  {user.username} left the room")
      
      except Exception as e:
         print(f"An error on user_on_join: {e}") 
      
    
    async def teleport_user_next_to(self, target_username: str, requester_user: User):
      room_users = await self.highrise.get_room_users()
      requester_position = None

      for user, position in room_users.content:
        if user.id == requester_user.id:
            requester_position = position
            break
      for user, position in room_users.content:
        if user.username.lower() == target_username.lower(): 
          z = requester_position.z 
          new_z = z + 1 

          user_dict = {
            "id": user.id,
            "position": Position(requester_position.x, requester_position.y, new_z, requester_position.facing)
          }
          await self.highrise.teleport(user_dict["id"], user_dict["position"])

   

   
    async def userinfo (self: BaseBot, user: User, message: str) -> None:
      #Split the message into parts
      parts = message.split(" ")
      if len(parts) != 2:
          await self.highrise.chat("Incorrect format, please use /userinfo <@username>")
          return
      #Removes the @ from the username if it exists
      if parts[1].startswith("@"):
          username = parts[1][1:]
      else:
          username = parts[1]
      #Get the user id from the username
      user = await self.webapi.get_users(username = username, limit=1)
      if user:
          user_id = user.users[0].user_id
      else:
          await self.highrise.chat("User not found, please specify a valid user")
          return

      #Get the user info
      userinfo = await self.webapi.get_user(user_id)
      number_of_followers = userinfo.user.num_followers
      number_of_friends = userinfo.user.num_friends
      number_of_folowing = userinfo.user.num_following
      joined_at = (userinfo.user.joined_at).strftime("%d/%m/%Y %H:%M:%S")
      try:
          last_login = (userinfo.user.last_online_in).strftime("%d/%m/%Y %H:%M:%S")
      except:
          last_login = "Last login not available"
      #Get the number of posts and the most liked post
      userposts = await self.webapi.get_posts(author_id = user_id)
      number_of_posts = 0
      most_likes_post = 0
      try:
          while userposts.last_id != "":
              for post in userposts.posts:
                  if post.num_likes > most_likes_post:
                      most_likes_post = post.num_likes
                  number_of_posts += 1
              userposts = await self.webapi.get_posts(author_id = user_id, starts_after=userposts.last_id)
      except Exception as e:
          print (e)

      #Send the info to the chat
      await self.highrise.chat(f"""\nUser: {username}\nNumber of followers: {number_of_followers}\nNumber of friends: {number_of_friends}\nNumber of following: {number_of_folowing}\nJoined at: {joined_at}\nLast login: {last_login}\nNumber of posts: {number_of_posts}\nMost likes in a post: {most_likes_post}""")
    
    async def run(self, room_id, token):
        definitions = [BotDefinition(self, room_id, token)]
        await __main__.main(definitions) 
    

    def remaining_time(self, username):
        if username in self.temporary_vips:
            remaining_seconds = self.temporary_vips[username] - int(time.time())
            if remaining_seconds > 0:
                return str(timedelta(seconds=remaining_seconds))
        return "Not a temporary VIP."


    async def on_chat(self, user: User, message: str) -> None:
      try:
         user_input = None
    
         
         if message.lower().startswith("-announce "):
           if user.username.lower() in self.moderators:
             parts = message.split()
             if len(parts) >= 3:
                user_input =  message[len("-announce "):]
                await self.highrise.chat( "Alright i will loop with with intervals of 60 seconds")
                await self.announce(user_input,message)
         if message.lower().startswith("-clear") and user.username.lower() in owners :
            if user.username.lower() in self.moderators:
               await self.highrise.chat (f"Announcement message cleared")
               self.stop_announce()
               return
         if  message.lower().startswith("wallet"):
            if user.username.lower() in self.moderators :

                  wallet = (await self.highrise.get_wallet()).content
                  await self.highrise.send_whisper(user.id, f"The bot wallet contains {wallet[0].amount} {wallet[0].type}")

            else: 
                await  self.highrise.send_whisper(user.id, f"Only Moderators Can View the Wallet")       
         if message.startswith("❤️ all"):
           if user.username.lower() in self.moderators:
             roomUsers = (await self.highrise.get_room_users()).content
             for roomUser, _ in roomUsers:
                await self.highrise.react("heart", roomUser.id)
         if message.startswith("!kick"):
            if user.username.lower() in self.moderators:
                parts = message.split()
                if len(parts) < 2:
                    await self.highrise.chat(user.id, "Usage: !kick @username")
                    return

                mention = parts[1]
                username_to_kick = mention.lstrip('@')  # Remove the '@' symbol from the mention
                response = await self.highrise.get_room_users()
                users = [content[0] for content in response.content]  # Extract the User objects
                user_ids = [user.id for user in users]  # Extract the user IDs

                if username_to_kick.lower() in [user.username.lower() for user in users]:
                    user_index = [user.username.lower() for user in users].index(username_to_kick.lower())
                    user_id_to_kick = user_ids[user_index]
                    await self.highrise.moderate_room(user_id_to_kick, "kick")
                    await self.highrise.chat( f"Kicked {mention}.")
                else:
                    await self.highrise.send_whisper(user.id, f"User {mention} is not in the room.")
            else:
                await self.highrise.send_whisper(user.id, "You can't use this command.")

         elif message.startswith("!mute"):
            if user.username.lower() in self.moderators:
                parts = message.split()
                if len(parts) < 2:
                    await self.highrise.chat(user.id, "Usage: !mute @username")
                    return

                mention = parts[1]
                username_to_mute = mention.lstrip('@')  # Remove the '@' symbol from the mention
                response = await self.highrise.get_room_users()
                users = [content[0] for content in response.content]  # Extract the User objects
                user_ids = [user.id for user in users]  # Extract the user IDs

                if username_to_mute.lower() in [user.username.lower() for user in users]:
                    user_index = [user.username.lower() for user in users].index(username_to_mute.lower())
                    user_id_to_mute = user_ids[user_index]
                    await self.highrise.moderate_room(user_id_to_mute, "mute",3600)  # Mute for 1 hour
                    await self.highrise.chat(f"Muted {mention} for 1 hour.")
                else:
                    await self.highrise.send_whisper(user.id, f"User {mention} is not in the room.")
            else:
                await self.highrise.send_whisper(user.id, "You can't use this command.")

         elif message.startswith("!unmute"):
            if user.username.lower() in self.moderators:
                parts = message.split()
                if len(parts) < 2:
                    await self.highrise.chat(user.id, "Usage: !mute @username")
                    return

                mention = parts[1]
                username_to_mute = mention.lstrip('@')  # Remove the '@' symbol from the mention
                response = await self.highrise.get_room_users()
                users = [content[0] for content in response.content]  # Extract the User objects
                user_ids = [user.id for user in users]  # Extract the user IDs

                if username_to_mute.lower() in [user.username.lower() for user in users]:
                    user_index = [user.username.lower() for user in users].index(username_to_mute.lower())
                    user_id_to_mute = user_ids[user_index]
                    await self.highrise.moderate_room(user_id_to_mute, "mute",1)  # Mute for 1 hour
                    await self.highrise.chat(f"{mention} Unmuted.")
                else:
                    await self.highrise.send_whisper(user.id, f"User {mention} is not in the room.")
            else:
                await self.highrise.send_whisper(user.id, "You can't use this command.")

         elif message.startswith("!ban"):
            if user.username.lower() in self.moderators:
                parts = message.split()
                if len(parts) < 2:
                    await self.highrise.chat(user.id, "Usage: !ban @username")
                    return

                mention = parts[1]
                username_to_ban = mention.lstrip('@')  # Remove the '@' symbol from the mention
                response = await self.highrise.get_room_users()
                users = [content[0] for content in response.content]  # Extract the User objects
                user_ids = [user.id for user in users]  # Extract the user IDs

                if username_to_ban.lower() in [user.username.lower() for user in users]:
                    user_index = [user.username.lower() for user in users].index(username_to_ban.lower())
                    user_id_to_ban = user_ids[user_index]
                    await self.highrise.moderate_room(user_id_to_ban, "ban", 3600)  # Ban for 1 hour
                    await self.highrise.chat(f"Banned {mention} for 1 hour.")
                else:
                    await self.highrise.send_whisper(user.id, f"User {mention} is not in the room.")
            else:
                await self.highrise.send_whisper(user.id, "You can't use this command.")

        
        
         if message == "!tip5":
              if user.username == "Devil_808" :
                roomUsers = (await self.highrise.get_room_users()).content
                for roomUser, _ in roomUsers:
                  await self.highrise.tip_user(roomUser.id, "gold_bar_5")
              else: 
                await  self.highrise.send_whisper(user.id, f"Only @Devil_808 can use tip!")

         if message == "!tip1":
              if user.username == "Devil_808":
                roomUsers = (await self.highrise.get_room_users()).content
                for roomUser, _ in roomUsers:
                  await self.highrise.tip_user(roomUser.id, "gold_bar_1")
              else: 
                await  self.highrise.send_whisper(user.id, f"Only the @Devil_808 can use tip!")

         if message.lstrip().startswith(("-give","-remove","-here","-tele")):
            response = await self.highrise.get_room_users()
            users = [content[0] for content in response.content]
            usernames = [user.username.lower() for user in users]
            parts = message[1:].split()
            args = parts[1:]

            if len(args) < 1:
                await self.highrise.send_whisper(user.id, f"Kullanım: !{parçalar[0]} <@Alionardo_>")
                return
            elif args[0][0] != "@":
                await self.highrise.send_whisper(user.id, "Invalid user format. Please use '@username'.")
                return
            elif args[0][1:].lower() not in usernames:
                await self.highrise.send_whisper(user.id, f"{args[0][1:]} is not in the room.")
                return

            user_id = next((u.id for u in users if u.username.lower() == args[0][1:].lower()), None)
            user_name = next((u.username.lower() for u in users if u.username.lower() == args[0][1:].lower()), None)
            if not user_id:
                await self.highrise.send_whisper(user.id, f"User {args[0][1:]} not found")
                return                     
            try:
                if message.lower().startswith("-give") and message.lower().endswith("vip"):   
                  if user.username.lower() in owners:
                     if user_name.lower() not in self.membership:
                        self.membership[user_name] = int(time.time()) + 24 * 60 * 60  
                        self.save_membership()
                        await self.highrise.chat(f"Congratulations! {user_name}you been given a \n🎫 Party vip ticket 🎫 \n ____________________________\nUse the key -vip  to teleport")

                elif message.lower().startswith("-give") and message.lower().endswith("mod"):   
                  if user.username.lower() in owners :
                     await self.highrise.chat(f"{user_name} is now a Permanent MOD, given by {user.username}")
                     if user_name.lower() not in self.moderators:
                           self.moderators.append(user_name)
                           self.save_moderators()
                elif message.lower().startswith("-give") and message.lower().endswith("mod 24h"):
                  if user.username.lower() in owners :
                     await self.highrise.chat(f"{user_name} is now a Temporary MOD, given by {user.username}")
                     if user_name not in self.temporary_vips:
                         self.temporary_vips[user_name] = int(time.time()) + 24 * 60 * 60  # VIP for 24 hours
                         self.save_temporary_vips()
                elif message.lower().startswith("-remove") and message.lower().endswith("mod"):
                  if user.username.lower() in owners :
                    if user_name in self.moderators:
                       self.moderators.remove(user_name)
                       self.save_moderators()
                       await self.highrise.chat(f"{user_name} is no longer a moderator.")
                elif message.lower().startswith("-here"):
                   if user.username.lower() in self.moderators:
                      target_username = user_name
                      if target_username not in owners :
                          await self.teleport_user_next_to(target_username, user)
                elif message.lower().startswith(('-tele')) and  message.lower().endswith("b1"):   
                  if user.username.lower() in self.moderators:
                    await self.highrise.teleport(user_id, Position(8.5, 11.25,1.5))
                elif message.lower().startswith(('-tele')) and  message.lower().endswith("b2"):   
                  if user.username.lower() in self.moderators:
                    await self.highrise.teleport(user_id, Position(15.5, 14.75,10.5))
                elif message.lower().startswith(('-tele')) and  message.lower().endswith("b3"):   
                  if user.username.lower() in self.moderators:
                    await self.highrise.teleport(user_id, Position(14.5, 12.25,24.5))
                elif message.lower().startswith(('-tele')) and  message.lower().endswith("vip"):   
                  if user.username.lower() in self.moderators:
                    await self.highrise.teleport(user_id, Position(13.5, 6.25,4.5))
                elif message.lower().startswith(('-tele')) and  message.lower().endswith("dj"):   
                  if user.username.lower() in self.moderators:
                    await self.highrise.teleport(user_id, Position(16.5,13.75,1.5))
                elif message.lower().startswith(('-tele')) and  message.lower().endswith("g"):   
                  if user.username.lower() in self.moderators:
                     await self.highrise.teleport(user_id, Position(11,0.5,10.5))
              
            except Exception as e:
                print(f"{e}")
         if message.lower().lstrip().startswith(("-emote", "!emote")):
                await self.highrise.send_whisper(user.id, "\n• Emote can be used by NUMBERS")
                await self.highrise.send_whisper(user.id, "\n• For loops say -loop or !loop")         
         if message.lower().lstrip().startswith(("!loop","-loop")):
            await self.highrise.send_whisper(user.id,"\n• loops\n ____________________________\nMention loop before the emote numer\n ____________________________")
            await self.highrise.send_whisper(user.id,"I have sent you details in private chat.")  

         if message.lower().lstrip().startswith(("-list", "!list")):
                await self.highrise.chat("\\commands you can use:\n• !feedback or -feedback \n• !teleport or -teleport\n• !loop or -loop \n• !emote or -emote\n• -buy or !buy for \n 🎫VIP Tickets🎫 ")
                await self.highrise.chat(f"\n ____________________________\n• !mod or -mod ( only for mods )")
         if message.lower().lstrip().startswith(("-buy" , "!buy")):
             await self.highrise.chat(f"\n  vip = 100 per month 🎫 \nTip 100 to bot you will be aceessed to use vip tele commands. ")
        
     
         if message.lower().lstrip().startswith(("-teleport", "!teleport")):
                    await self.highrise.chat(f"\n • Teleports\n ____________________________\nGround floor : -g  \n-vip : (vip only)\n-dj : (only mods)\n-top : (only mods), make sure you have 🎫VIP Tickets 🎫 \n• type -buy or !buy for details ")
         if message.lower().lstrip().startswith(("!rules", "-rules")):
               await self.highrise.chat(f"\n\n        RULES\n ____________________________\n 1. NO UNDERAGE \n 2. No advertising\n 3. No hate speech \n 4. No begging (those trash will be immediately banned 🚫) \n 5. No spamming ")
         if message.lower().lstrip().startswith(("-feedback", "!feedback")):
                    await self.highrise.send_whisper(user.id, "• [ Submit Feedback ]\\Thank you for joining our room! \n We value your feedback,")
                    await self.highrise.send_whisper(user.id,"Please share your feedback/suggestions with @x_softangel_x to improve our environment. Your contributions are valuable and will help us improve.")  

         if user.username.lower() in self.moderators:
            if message.lower().lstrip().startswith(("-admin list","!admin list")):
               await self.highrise.send_whisper(user.id,"\n  \n•Moderating :\n ____________________________\n !kick @ \n !ban @ \n !mute @ \n !unmute @ ")
               await self.highrise.send_whisper(user.id,"\n  \n•Teleporting :\n ____________________________\n-tele @ teleport key .\nTeleport keys :\nvip ,dj ,top ,g (for ground)\n\nExample -tele @username vip \n\n-here @ :to summon.")
         if message.lstrip().startswith(("!prof","-prof", "!profile", "-profile")) and user.username.lower().startswith:
              await self.userinfo (user, message) 
         if message.lower().startswith('-b1') :
           if user.username.lower() in self.moderators:    
              await self.highrise.teleport(f"{user.id}", Position(8.5, 11.25,1.5))
         if message.lower().startswith('-b2') :
           if user.username.lower() in self.moderators:    
              await self.highrise.teleport(f"{user.id}", Position(15.5, 14.75, 10.5))
         if message.lower().startswith('-b3') :
           if user.username.lower() in self.moderators:    
              await self.highrise.teleport(f"{user.id}", Position(14.5, 12.25,24.5))
         if message.lower().startswith('-vip') :
           if user.username.lower() in self.moderators or user.username.lower() in self.membership :  
               await self.highrise.teleport(f"{user.id}", Position(13.5, 6.25,4.5))
           else:
             await self.highrise.send_whisper((user.id)," this is a privet place for VIPs , uou can use it by purchaseing VIP Ticket type -buy")
         if message.lower().startswith('-dj') :
            if user.username.lower() in self.moderators:    
              await self.highrise.teleport(f"{user.id}", Position(16.5,13.75,1.5))
         if message == "-g" or message == "-g ":
              await self.highrise.teleport(f"{user.id}", Position(11,0.5,10.5))
           
         if message.lower().startswith("loop"):
           parts = message.split()
           E = parts[1]
           E = int(E)
           emote_text, emote_time = await self.get_emote_E(E)
           emote_time -= 1
           user_id = user.id  
           if user.id in self.continuous_emote_tasks and not self.continuous_emote_tasks[user.id].cancelled():
              await self.stop_continuous_emote(user.id)
              task = asyncio.create_task(self.send_continuous_emote(emote_text,user_id,emote_time))
              self.continuous_emote_tasks[user.id] = task
           else:
              task = asyncio.create_task(self.send_continuous_emote(emote_text,user_id,emote_time))
              self.continuous_emote_tasks[user.id] = task  

         elif message.lower().startswith("stop"):
            if user.id in self.continuous_emote_tasks and not self.continuous_emote_tasks[user.id].cancelled():
                await self.stop_continuous_emote(user.id)
                await self.highrise.chat("Continuous emote has been stopped.")
            else:
                await self.highrise.chat("You don't have an active loop_emote.")
         elif message.lower().startswith("users"):
            room_users = (await self.highrise.get_room_users()).content
            await self.highrise.chat(f"There are {len(room_users)} users in the room")
 
         if  message.isdigit() and 1 <= int(message) <= 91:
              parts = message.split()
              E = parts[0]
              E = int(E)
              emote_text, emote_time = await self.get_emote_E(E)    
              tasks = [asyncio.create_task(self.highrise.send_emote(emote_text, user.id))]
              await asyncio.wait(tasks)  
         if message.startswith("/e1"):
                 await self.highrise.set_outfit(outfit=[
          Item(type='clothing', 
                    amount=1, 
                    id='body-flesh',
                    account_bound=False,
                    active_palette=12),
          Item(type='clothing',
                    amount=1,
                    id='shirt-n_starteritems2019raglanwhite',
                   account_bound=False,
                    active_palette=-1),
          Item(type='clothing', 
               amount=1, 
               id='pants-n_room12019blackacidwashjeans',
               account_bound=False,
               active_palette=-1),
          Item(type='clothing', 
               amount=1, 
               id='nose-n_01_b',
               account_bound=False,
               active_palette=-1),
         Item(type='clothing',
              amount=1, 
              id='watch-n_room32019blackwatch', 
              account_bound=False,
              active_palette=-1),
         Item(type='clothing', 
              amount=1, 
              id='watch-n_room32019blackwatch', 
              account_bound=False,
              active_palette=-1),
         Item(type='clothing', 
              amount=1, id='shoes-n_room22019tallsocks', 
              account_bound=False,
              active_palette=-1), 
         Item(type='clothing',
              amount=1, 
              id='shoes-n_converse_black',
              account_bound=False,
              active_palette=-1),       
         Item(type='clothing',
              amount=1, 
              id='freckle-n_basic2018freckle22', 
              account_bound=False,
              active_palette=-1),
         Item(type='clothing',
              amount=1,
              id='mouth-basic2018smirk',
              account_bound=False,
              active_palette=3),
         Item(type='clothing',
              amount=1,
              id= 'hair_back-n_malenew01',
              account_bound=False, active_palette=70),
        Item(type='clothing',
              amount=1,
              id= 'hair_front-n_malenew01',
              account_bound=False, active_palette=70),  
         Item(type='clothing', 
              amount=1, 
              id='eye-n_basic2018malediamondsleepy',
              account_bound=False,
              active_palette=2),
        Item(type='clothing', 
             amount=1,
             id='eyebrow-n_06', 
             account_bound=False,
             active_palette=-1)
      ])

         if  message.lower().startswith("wallet"):
            if user.username.lower() in self.moderators :

                  wallet = (await self.highrise.get_wallet()).content
                  await self.highrise.send_whisper(user.id, f"The bot wallet contains {wallet[0].amount} {wallet[0].type}")

            else: 
                await  self.highrise.send_whisper(user.id, f"Only Moderators Can View the Wallet")

    
          
      except Exception as e:
        print(f"An exception occured: {e}")  

    async def send_continuous_emote(self, emote_text ,user_id,emote_time):
      try:
          while True:                    
                tasks = [asyncio.create_task(self.highrise.send_emote(emote_text, user_id))]
                await asyncio.wait(tasks)
                await asyncio.sleep(emote_time)
                await asyncio.sleep(1)
      except Exception as e:
                print(f"{e}")

  
    async def stop_continuous_emote(self, user_id: int):
      if user_id in self.continuous_emote_tasks and not self.continuous_emote_tasks[user_id].cancelled():
          task = self.continuous_emote_tasks[user_id]
          task.cancel()
          with contextlib.suppress(asyncio.CancelledError):
              await task
          del self.continuous_emote_tasks[user_id]

    async def follow_user(self, target_username: str):
      while self.following_username == target_username:

          response = await self.highrise.get_room_users()
          target_user_position = None
          for user_info in response.content:
              if user_info[0].username.lower() == target_username.lower():
                  target_user_position = user_info[1]
                  break

          if target_user_position:
              nearby_position = Position(target_user_position.x + 1.0, target_user_position.y, target_user_position.z)
              await self.highrise.walk_to(nearby_position)

              await asyncio.sleep(2)
    async def get_emote_E(self, target) -> None: 

     try:
        emote_info = self.Emotes.get(target)
        return emote_info
     except ValueError:
        pass
    async def on_whisper(self, user: User, message: str ) -> None:
     try:
        
       
        if message.startswith("!time"):
            parts = message.split()
            if len(parts) == 2:
                target_mention = parts[1]

                # Remove the "@" symbol if present
                target_user = target_mention.lstrip('@')

                # Check if the target user has temporary VIP status
                remaining_time = self.remaining_time(target_user.lower())
                await self.highrise.send_whisper(user.id, f"Remaining time for {target_mention}'s temporary VIP status: {remaining_time}")
            else:
                await self.highrise.send_whisper(user.id, "Usage: !time @username")


        if message.lstrip().startswith(("!prof","-prof", "!profile", "-profile")) and user.username.lower().startswith:
              await self.userinfo (user, message) 

           
        if message.lower().startswith("loop"):
           parts = message.split()
           E = parts[1]
           E = int(E)
           emote_text, emote_time = await self.get_emote_E(E)
           emote_time -= 1
           user_id = user.id  
           if user.id in self.continuous_emote_tasks and not self.continuous_emote_tasks[user.id].cancelled():
              await self.stop_continuous_emote(user.id)
              task = asyncio.create_task(self.send_continuous_emote(emote_text,user_id,emote_time))
              self.continuous_emote_tasks[user.id] = task
           else:
              task = asyncio.create_task(self.send_continuous_emote(emote_text,user_id,emote_time))
              self.continuous_emote_tasks[user.id] = task  

        elif message.lower().startswith("stop"):
            if user.id in self.continuous_emote_tasks and not self.continuous_emote_tasks[user.id].cancelled():
                await self.stop_continuous_emote(user.id)
                await self.highrise.chat("Continuous emote has been stopped.")
            else:
                await self.highrise.chat("You don't have an active loop_emote.")
        elif message.lower().startswith("users"):
            room_users = (await self.highrise.get_room_users()).content
            await self.highrise.chat(f"There are {len(room_users)} users in the room")

        if  message.isdigit() and 1 <= int(message) <= 91:
              parts = message.split()
              E = parts[0]
              E = int(E)
              emote_text, emote_time = await self.get_emote_E(E)    
              tasks = [asyncio.create_task(self.highrise.send_emote(emote_text, user.id))]
              await asyncio.wait(tasks)
        
        if message == "-here":
            if user.username.lower() in self.moderators:
                response = await self.highrise.get_room_users()
                users = [content for content in response.content]
                for u in users:
                    if u[0].id == user.id:
                        try:
                            await self.highrise.teleport(Counter.bot_id,Position((u[1].x),(u[1].y),(u[1].z),"FrontRight"))


                            break
                        except:

                            pass
       
        if message.startswith("-say"):
            if user.username.lower() in self.moderators:
                text = message.replace("-say", "").strip()
                await self.highrise.chat(text)

   
         

        elif message.startswith("-come"):
            if user.username.lower() in self.moderators:
                response = await self.highrise.get_room_users()
                your_pos = None
                for content in response.content:
                    if content[0].id == user.id:
                        if isinstance(content[1], Position):
                            your_pos = content[1]
                            break
                if not your_pos:
                    await self.highrise.send_whisper(user.id, "Invalid coordinates!")
                    return
                await self.highrise.chat(f"@{user.username} I'm coming ..")
                await self.highrise.walk_to(your_pos)

        elif message.lower().startswith("-follow"):
         
            target_username = message.split("@")[1].strip()

            if target_username.lower() == self.following_username:
                await self.highrise.send_whisper(user.id,"I am already following.")
            elif message.startswith("-say"):
              if user.username.lower() in self.moderators:
                  text = message.replace("-say", "").strip()
                  await self.highrise.chat(text)
            else:
                self.following_username = target_username
                await self.highrise.chat(f"hey {target_username}.")
            
                await self.follow_user(target_username)
        elif message.lower() == "-stop following":
            self.following_username = None
          
            await self.highrise.walk_to(Position(2.5,0.25,4.5,"FrontRight"))

  
     except Exception as e:
             print(f"An exception occured: {e}")
              
    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        try:
            print(f"{sender.username} tipped {receiver.username} an amount of {tip.amount}")
            await self.highrise.chat(f"𝓣𝓱𝓮 𝓐𝓶𝓪𝔃𝓲𝓷𝓰 {sender.username} 𝓽𝓲𝓹𝓹𝓮𝓭 {receiver.username} 𝓪𝓷 𝓪𝓶𝓸𝓾𝓷𝓽 𝓸𝓯  {tip.amount}𝐆𝐎𝐋𝐃")

            
       
            if tip.amount == 100:
              if receiver.id== Counter.bot_id:    
                 sender_username = sender.username.lower()
                 if sender_username not in self.membership:
                   self.membership[sender_username] = int(time.time()) + 24 * 60 * 60  
                   self.save_membership()
                   await self.highrise.chat(f"Thank you {sender_username} for purchasing TRMPORARY vip ticket , now u can use the command -vip to teleport to the vip now \n-vip: to go vip place🎫 . \n-g:ground floor") 

                 
        except Exception as e:
             print(f"An exception occured: {e}")

  
  




    
