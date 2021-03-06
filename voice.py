# coding=utf-8
"""
DecoraterBot's Voice Channel Plugin.
"""
import json
import sys
import os

import youtube_dl
import discord
from discord.ext import commands
from DecoraterBotUtils import BotErrors
from DecoraterBotUtils.utils import *


def make_voice_info(server_id, textchannel_id,
                    voice_id):
    """
    Makes the Text, Voice Channel, and Server objects
    with the cached id's for Voice Channels.
    """
    serverobj = discord.server.Server(id=server_id)
    textchannelobj = discord.channel.Channel(
        server=serverobj, id=textchannel_id)
    voicechannelobj = discord.channel.Channel(
        server=serverobj, id=voice_id)
    return voicechannelobj, textchannelobj


class VoiceChannel:
    """
    Class that should hopefully catch states
    for all voice channels the bot joins in on.
    """
    def __init__(self, bot, botvoicechannel,
                 voicechannelobj, textchannelobj):
        """
        Creates an instance of the VoiceChannel object
        to use in with the Voice Commands.

        This requires that voicechannelobj and textchannelobj
        are channel objects. This means making the objects when
        bot restarts on voice channel rejoins.

        :param voicechannelobj: Object to the Voice Channel
            the VoiceChannel object is for.
        :param textchannelobj:  Object to the Text Channel
            the VoiceChannel object is for.
        """
        self.bot = bot
        self.botvoicechannel = botvoicechannel
        self.vchannel = voicechannelobj
        self.voice_message_channel = textchannelobj
        self.voice_message_server = textchannelobj.server
        self.voice = None
        self._sent_finished_message = False
        self.is_bot_playing = False
        # to replace the temp player and normal player crap soon.
        self.player_list = []
        # denotes if an error happened while joining the
        # Voice Channel.
        self.verror = False

    async def join(self):
        """
        Joins the particular voice channel.
        """
        if self.voice_message_server.id not in \
                self.botvoicechannel:
            self.botvoicechannel[
                self.voice_message_server.id] = {}
        if self.voice_message_channel.id not in \
                self.botvoicechannel:
            self.botvoicechannel[
                self.voice_message_server.id
            ]['text'] = self.voice_message_channel.id
        if self.vchannel.id not in self.botvoicechannel:
            self.botvoicechannel[
                self.voice_message_server.id
            ]['voice'] = self.vchannel.id
        self.write_json()
        self.voice = await self.bot.join_voice_channel(
            self.vchannel)

    def write_json(self):
        """
        writes the data to file.
        """
        file_name = os.path.join(
            sys.path[0], 'resources', 'ConfigData',
            'BotVoiceChannel.json')
        json.dump(self.botvoicechannel, open(file_name, "w"))

    def add_player(self, player):
        """
        Adds an player to the Voice Channel list.

        Note: All finished / stopped players must
        be removed from the list to prevent breakage
        of this cog. To do that cache the current player
        before starting and then when it is
        finished / stopped remove it by calling
        remove_player.
        """
        # cap list at 15 players per instance.
        if len(self.player_list) < 15:
            self.player_list.append(player)
        else:
            raise BotErrors.MaxPlayersError(
                "The maximum number of players for this"
                " Voice Channel has been reached.")

    def remove_player(self, player):
        """
        Adds an player to the Voice Channel list.
        """
        self.player_list.remove(player)

    async def leave(self):
        """
        Leaves the particular voice channel.
        """
        # Hopefully this assumption is correct.
        self.botvoicechannel.pop(
            self.voice_message_server.id)
        self.write_json()
        try:
            await self.voice.disconnect()
        except ConnectionResetError:
            # Supress a Error here.
            pass

    async def move(self, voicechannelobj):
        """
        Move to an particular voice channel.

        :param voicechannelobj: Voice Channel
            object to move to.
        """
        self.vchannel = voicechannelobj
        if self.vchannel.id not in self.botvoicechannel:
            self.botvoicechannel[
                self.voice_message_server.id
            ]['voice'] = self.vchannel.id
        self.write_json()
        await self.voice.move_to(self.vchannel)

    async def create_player(self, *args, **kwargs):
        """
        Handles creating all the player stuff for me.

        This helps makes this class easier for the
        rewrite to use.
        """
        await self.add_player(
            await self.voice.create_ytdl_player(
                *args, **kwargs))


class Voice:
    """
    Voice Channel Commands class for DecoraterBot.
    """
    def __init__(self, bot):
        self.bot = bot
        self.botvoicechannel = PluginConfigReader(
            file='BotVoiceChannel.json')
        # this will remain the same.
        self.ytdlo = {
            'verbose': False,
            'logger': YTDLLogger(self.bot),
            'default_search': "ytsearch"
        }
        # list of VoiceChannel class instances to keep track of them all.
        self.voiceobjs = []
        # deprecated, see VoiceChannel.player_list instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self.player = None
        # deprecated, see VoiceChannel.vchannel instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self.vchannel = None
        # deprecated, see VoiceChannel.vchannel instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self.vchannel_name = None
        # deprecated, see VoiceChannel.voice_message_channel
        # instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self.voice_message_channel = None
        # deprecated, see VoiceChannel.voice_message_server
        # instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self.voice_message_server = None
        # deprecated, see VoiceChannel.voice_message_server
        # instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self.voice_message_server_name = None
        # deprecated, see VoiceChannel.voice instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self.voice = None
        # deprecated, see VoiceChannel._sent_finished_message
        # instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self._sent_finished_message = False
        # deprecated, see VoiceChannel.is_bot_playing instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self.is_bot_playing = False
        # deprecated, see VoiceChannel.bot_playlist instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self.bot_playlist = []
        # deprecated, see VoiceChannel.bot_playlist_entries
        # instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self.bot_playlist_entries = []
        # deprecated, see VoiceChannel.player_list instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self._temp_player_1 = None
        # deprecated, see VoiceChannel.player_list instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self._temp_player_2 = None
        # deprecated, see VoiceChannel.player_list instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self._temp_player_3 = None
        # deprecated, see VoiceChannel.player_list instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self._temp_player_4 = None
        # deprecated, see VoiceChannel.player_list instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self._temp_player_5 = None
        # deprecated, see VoiceChannel.player_list instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self._temp_player_6 = None
        # deprecated, see VoiceChannel.player_list instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self._temp_player_7 = None
        # deprecated, see VoiceChannel.player_list instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self._temp_player_8 = None
        # deprecated, see VoiceChannel.player_list instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self._temp_player_9 = None
        # deprecated, see VoiceChannel.player_list instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self._temp_player_10 = None
        # this will remain the same.
        self.ffmop = "-nostats -loglevel quiet"
        # deprecated, see VoiceChannel.verror instead.
        # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!
        self.verror = False
        # Global bool to prevent the bot from being able to join a voice channel
        # while logging in. This is Essentially a fix to the bot not being able
        # to actually send messages in the voice commands as they would
        # drastically screw up.
        self.lock_join_voice_channel_command = False
        # For loading Voice Channel message data.
        self.voice_text = PluginTextReader(
            file='voice.json')
        self.resolve_send_message_error = (
            self.bot.BotPMError.resolve_send_message_error)
        self.rsme = self.resolve_send_message_error

    def setup(self):
        """
        Allows bot to rejoin voice channel when reloading.
        """
        self.bot.loop.create_task(self.__load())

    # will be revised on next release of this cog!!!

    async def __load(self):
        """
        Makes bot able to join a voice channel when the commands are loaded.
        """
        try:
            vchannel_2 = str(
                self.botvoicechannel['Bot_Current_Voice_Channel'][0])
            vmserver = str(
                self.botvoicechannel['Bot_Current_Voice_Channel'][1])
            vmchannel = str(
                self.botvoicechannel['Bot_Current_Voice_Channel'][2])
            self.voice_message_server_name = str(
                self.botvoicechannel['Bot_Current_Voice_Channel'][3])
            self.vchannel_name = str(
                self.botvoicechannel['Bot_Current_Voice_Channel'][4])
            self.vchannel = discord.Object(id=vchannel_2)
            self.voice_message_server = discord.Object(id=vmserver)
            self.voice_message_channel = discord.Object(id=vmchannel)
            try:
                self.voice = await self.bot.join_voice_channel(self.vchannel)
                self.verror = False
            except discord.ConnectionClosed:
                pass
            except discord.InvalidArgument:
                self.voice_message_server_name = None
                self.vchannel_name = None
                self.vchannel = None
                self.voice_message_server = None
                self.voice_message_channel = None
                self.voice = None
                self.verror = True
            except BotErrors.CommandTimeoutError:
                await self.bot.send_message(self.voice_message_channel,
                                            content=str(
                                                self.voice_text[
                                                    'reload_commands_vo'
                                                    'ice_channels_bypass2'][
                                                    0]))
                self.voice_message_server_name = None
                self.vchannel_name = None
                self.vchannel = None
                self.voice_message_server = None
                self.voice_message_channel = None
                self.voice = None
                self.verror = True
            except RuntimeError:
                self.voice_message_server_name = None
                self.vchannel_name = None
                self.vchannel = None
                self.voice_message_server = None
                self.voice = None
                self.verror = True
                msgdata = str(self.voice_text[
                                  'reload_commands_voice_channels_bypass2'][1])
                await self.bot.send_message(self.voice_message_channel,
                                            content=msgdata)
                self.voice_message_channel = None
            if self.verror is not True:
                message_data = str(
                    self.voice_text[
                        'reload_commands_voice_channels_bypass2'
                    ][2]).format(self.vchannel_name)
                await self.bot.send_message(self.voice_message_channel,
                                            content=message_data)
        except IndexError:
            self.voice_message_server_name = None
            self.vchannel_name = None
            self.vchannel = None
            self.voice_message_server = None
            self.voice_message_channel = None
            self.voice = None
        except discord.ClientException:
            # already in a voice channel so lots not set those
            # values to None.
            pass

    def __unload(self):
        """
        Makes bot able to leave Voice channel when reloading or unloading
        voice commands.
        """
        self.bot.loop.create_task(self.__reload())

    # will be revised on next release of this cog!!!

    async def __reload(self):
        """
        Makes bot able to leave Voice channel when reloading or unloading
        voice commands.
        """
        try:
            if self.voice is not None:
                await self.voice.disconnect()
                if self.voice_message_channel is not None:
                    try:
                        reason = str(
                            self.voice_text[
                                'reload_commands_voice_channels_bypass1'
                            ][1])
                        try:
                            message_data = str(
                                self.voice_text[
                                    'reload_commands_voice_channels_bypass1'][
                                    0]).format(
                                self.vchannel.name, reason)
                        except AttributeError:
                            message_data = str(
                                self.voice_text[
                                    'reload_commands_voice_channels_bypass1'][
                                    0]).format(
                                self.vchannel_name, reason)
                        await self.bot.send_message(self.voice_message_channel,
                                                    content=message_data)
                        self.voice_message_channel = None
                        self.voice = None
                        self.vchannel = None
                        self.voice_message_server = None
                        self.player = None
                        self.vchannel_name = None
                        self._sent_finished_message = False
                        self.voice_message_server_name = None
                        self.is_bot_playing = False
                    except discord.Forbidden:
                        pass
        except Exception as e:
            str(e)
            return

    # deprecated, see VoiceChannel.player_list.
    # WILL BE REMOVED ON NEXT RELEASE OF THIS COG!!!

    def resolve_bot_playlist_issue(self):
        """
        This should fix the Memory leaks of ffmpeg processes from the temp
        players when a song stops playing.
        """
        if self.is_bot_playing is False:
            if self._temp_player_1 is not None:
                self._temp_player_1.start()
                self._temp_player_1.stop()
                self._temp_player_1 = None
            if self._temp_player_2 is not None:
                self._temp_player_2.start()
                self._temp_player_2.stop()
                self._temp_player_2 = None
            if self._temp_player_3 is not None:
                self._temp_player_3.start()
                self._temp_player_3.stop()
                self._temp_player_3 = None
            if self._temp_player_4 is not None:
                self._temp_player_4.start()
                self._temp_player_4.stop()
                self._temp_player_4 = None
            if self._temp_player_5 is not None:
                self._temp_player_5.start()
                self._temp_player_5.stop()
                self._temp_player_5 = None
            if self._temp_player_6 is not None:
                self._temp_player_6.start()
                self._temp_player_6.stop()
                self._temp_player_6 = None
            if self._temp_player_7 is not None:
                self._temp_player_7.start()
                self._temp_player_7.stop()
                self._temp_player_7 = None
            if self._temp_player_8 is not None:
                self._temp_player_8.start()
                self._temp_player_8.stop()
                self._temp_player_8 = None
            if self._temp_player_9 is not None:
                self._temp_player_9.start()
                self._temp_player_9.stop()
                self._temp_player_9 = None
            if self._temp_player_10 is not None:
                self._temp_player_10.start()
                self._temp_player_10.stop()
                self._temp_player_10 = None

    # will be revised on next release of this cog!!!

    async def on_ready(self):
        """
        When Bot is ready.
        """
        if self.bot.initial_rejoin_voice_channel:
            self.bot.initial_rejoin_voice_channel = False
            self.lock_join_voice_channel_command = True
            try:
                vchannel_2 = str(
                    self.botvoicechannel['Bot_Current_Voice_Channel'][0])
                vmserver = str(
                    self.botvoicechannel['Bot_Current_Voice_Channel'][1])
                vmchannel = str(
                    self.botvoicechannel['Bot_Current_Voice_Channel'][2])
                self.voice_message_server_name = str(
                    self.botvoicechannel['Bot_Current_Voice_Channel'][3])
                self.vchannel_name = str(
                    self.botvoicechannel['Bot_Current_Voice_Channel'][4])
                self.vchannel = discord.Object(id=vchannel_2)
                self.voice_message_server = discord.Object(id=vmserver)
                self.voice_message_channel = discord.Object(id=vmchannel)
                try:
                    self.voice = await self.bot.join_voice_channel(
                        self.vchannel)
                    self.verror = False
                except discord.ConnectionClosed:
                    pass
                except BotErrors.CommandTimeoutError:
                    self.voice_message_server_name = None
                    self.vchannel_name = None
                    self.vchannel = None
                    self.voice_message_server = None
                    self.voice_message_channel = None
                    self.voice = None
                    self.verror = True
                    self.lock_join_voice_channel_command = False
                except discord.InvalidArgument:
                    self.voice_message_server_name = None
                    self.vchannel_name = None
                    self.vchannel = None
                    self.voice_message_server = None
                    self.voice_message_channel = None
                    self.voice = None
                    self.verror = True
                    self.lock_join_voice_channel_command = False
                except RuntimeError:
                    self.voice_message_server_name = None
                    self.vchannel_name = None
                    self.vchannel = None
                    self.voice_message_server = None
                    self.voice_message_channel = None
                    self.voice = None
                    self.verror = True
                    self.lock_join_voice_channel_command = False
                    msgdata = str(
                        self.voice_text[
                            'reload_commands_voice_channels_bypass2'
                        ][1])
                    await self.bot.send_message(self.voice_message_channel,
                                                content=msgdata)
                if self.verror is not True:
                    message_data = str(
                        self.voice_text[
                            'reload_commands_voice_channels_bypass2'
                        ][2]).format(self.vchannel_name)
                    await self.bot.send_message(self.voice_message_channel,
                                                content=message_data)
                    self.lock_join_voice_channel_command = False
            except IndexError:
                self.voice_message_server_name = None
                self.vchannel_name = None
                self.vchannel = None
                self.voice_message_server = None
                self.voice_message_channel = None
                self.voice = None
                self.lock_join_voice_channel_command = False

    # will be revised on next release of this cog!!!

    @commands.command(name='JoinVoiceChannel', pass_context=True, no_pm=True)
    async def join_voice_channel_command(self, ctx):
        """
        Bot Voice Command.
        :param ctx: Command Context.
        """
        if ctx.message.channel.id in self.bot.ignoreslist["channels"]:
            return
        if ctx.message.author.id in self.bot.banlist['Users']:
            return
        elif self.vchannel is not None:
            try:
                messagedata = str(
                    self.voice_text['join_voice_channel_command_data'][0])
                try:
                    message_data = messagedata.format(
                        self.voice_message_server.name)
                except AttributeError:
                    message_data = messagedata.format(
                        self.voice_message_server_name)
                await self.bot.send_message(ctx.message.channel,
                                            content=message_data)
            except discord.Forbidden:
                await self.bot.BotPMError.resolve_send_message_error(self.bot,
                                                                     ctx)
        else:
            if not self.lock_join_voice_channel_command:
                self.voice_message_channel = ctx.message.channel
                self.voice_message_server = ctx.message.channel.server
                self.voice_message_server_name = (
                    ctx.message.channel.server.name)
                if ctx.message.author.voice_channel is not None:
                    self.vchannel = ctx.message.author.voice_channel
                    self.vchannel_name = ctx.message.author.voice_channel.name
                    if self.vchannel.id not in self.botvoicechannel:
                        self.botvoicechannel[
                            'Bot_Current_Voice_Channel'].append(
                            self.vchannel.id)
                    if self.voice_message_server.id not in \
                            self.botvoicechannel:
                        self.botvoicechannel[
                            'Bot_Current_Voice_Channel'].append(
                            self.voice_message_server.id)
                    if self.voice_message_channel.id not in \
                            self.botvoicechannel:
                        self.botvoicechannel[
                            'Bot_Current_Voice_Channel'].append(
                            self.voice_message_channel.id)
                    if self.voice_message_server_name not in \
                            self.botvoicechannel:
                        self.botvoicechannel[
                            'Bot_Current_Voice_Channel'].append(
                            self.voice_message_server_name)
                    if self.vchannel_name not in self.botvoicechannel:
                        self.botvoicechannel[
                            'Bot_Current_Voice_Channel'].append(
                            self.vchannel_name)
                    file_name = os.path.join(
                        sys.path[0], 'resources', 'ConfigData',
                       'BotVoiceChannel.json')
                    json.dump(self.botvoicechannel, open(file_name, "w"))
                    try:
                        try:
                            self.voice = await self.bot.join_voice_channel(
                                self.vchannel)
                        except discord.ConnectionClosed:
                            pass
                        except RuntimeError:
                            self.voice_message_server_name = None
                            self.vchannel_name = None
                            self.vchannel = None
                            self.voice_message_server = None
                            self.voice_message_channel = None
                            self.voice = None
                            self.verror = True
                            msgdata = str(
                                self.voice_text[
                                    'join_voice_channel_command_data'
                                ][6])
                            await self.bot.send_message(
                                self.voice_message_channel, content=msgdata)
                        if not self.verror:
                            try:
                                msg_data = str(
                                    self.voice_text[
                                        'join_voice_channel_command_data'
                                    ][1]).format(self.vchannel_name)
                                await self.bot.send_message(
                                    ctx.message.channel, content=msg_data)
                            except discord.Forbidden:
                                await self.resolve_send_message_error(
                                    self.bot, ctx)
                    except discord.InvalidArgument:
                        self.voice_message_channel = None
                        self.voice = None
                        self.vchannel = None
                        self.voice_message_server = None
                        self.voice_message_server_name = None
                        self.vchannel_name = None
                        try:
                            msg_data = str(
                                self.voice_text[
                                    'join_voice_channel_command_data'
                                ][2])
                            await self.bot.send_message(ctx.message.channel,
                                                        content=msg_data)
                        except discord.Forbidden:
                            await self.resolve_send_message_error(
                                self.bot, ctx)
                    except BotErrors.CommandTimeoutError:
                        self.voice_message_channel = None
                        self.voice = None
                        self.vchannel = None
                        self.voice_message_server = None
                        self.voice_message_server_name = None
                        self.vchannel_name = None
                        try:
                            msg_data = str(
                                self.voice_text[
                                    'join_voice_channel_command_data'
                                ][3])
                            await self.bot.send_message(ctx.message.channel,
                                                        content=msg_data)
                        except discord.Forbidden:
                            await self.resolve_send_message_error(
                                self.bot, ctx)
                        self.verror = True
                    except discord.HTTPException:
                        self.voice_message_channel = None
                        self.voice = None
                        self.vchannel = None
                        self.voice_message_server = None
                        try:
                            msg_data = str(
                                self.voice_text[
                                    'join_voice_channel_command_data'
                                ][4])
                            await self.bot.send_message(ctx.message.channel,
                                                        content=msg_data)
                        except discord.Forbidden:
                            await self.resolve_send_message_error(
                                self.bot, ctx)
                    except discord.opus.OpusNotLoaded:
                        self.voice_message_channel = None
                        self.voice = None
                        self.vchannel = None
                        self.voice_message_server = None
                        self.voice_message_server_name = None
                        self.vchannel_name = None
                        try:
                            msg_data = str(
                                self.voice_text[
                                    'join_voice_channel_command_data'
                                ][5])
                            await self.bot.send_message(ctx.message.channel,
                                                        content=msg_data)
                        except discord.Forbidden:
                            await self.resolve_send_message_error(
                                self.bot, ctx)
                    except IndexError:
                        return

    # will be revised on next release of this cog!!!

    @commands.command(name='play', pass_context=True, no_pm=True)
    async def play_command(self, ctx):
        """
        Bot Voice Command.
        :param ctx: Command Context.
        """
        if ctx.message.channel.id in self.bot.ignoreslist["channels"]:
            return
        if ctx.message.author.id in self.bot.banlist['Users']:
            return
        elif self.is_bot_playing is False:
            if self.voice is not None:
                if self.voice_message_channel is not None:
                    if ctx.message.channel.id == self.voice_message_channel.id:
                        try:
                            data = ctx.message.content[
                                   len(ctx.prefix + "play "):].strip()
                            if data == "":
                                try:
                                    message_data = str(
                                        self.voice_text[
                                            'play_command_data'
                                        ][0])
                                    await self.bot.send_message(
                                        self.voice_message_channel,
                                        content=message_data)
                                except discord.Forbidden:
                                    await self.resolve_send_message_error(
                                        self.bot, ctx.message)
                            if data.rfind('https://') == -1 and data.rfind(
                                    'http://') == -1:
                                # lets try to do a search.
                                self.player = (
                                    await self.voice.create_ytdl_player(
                                        data, ytdl_options=self.ytdlo,
                                        options=self.ffmop,
                                        after=self.voice_playlist))
                                self._sent_finished_message = False
                                self.is_bot_playing = True
                                if self.player is not None:
                                    try:
                                        fulldir = self.player.duration
                                        minutes = str(int((fulldir / 60) % 60))
                                        seconds = str(int(fulldir % 60))
                                        if len(seconds) == 1:
                                            seconds = "0" + seconds
                                        try:
                                            message_data = str(
                                                self.voice_text[
                                                    'play_command_data'][
                                                    1]).format(
                                                str(self.player.title),
                                                str(self.player.uploader),
                                                minutes, seconds)
                                            await self.bot.send_message(
                                                self.voice_message_channel,
                                                content=message_data)
                                        except discord.Forbidden:
                                            await (
                                                (self
                                                 ).resolve_send_message_error(
                                                    self.bot,
                                                    ctx.message))
                                        try:
                                            self.player.start()
                                        except RuntimeError:
                                            pass
                                    except AttributeError:
                                        message_data = str(
                                            self.voice_text[
                                                'play_command_data'][2])
                                        self.is_bot_playing = False
                                        await self.bot.send_message(
                                            self.voice_message_channel,
                                            content=message_data)
                            else:
                                if '<' and '>' in data:
                                    data = data.strip('<')
                                    data = data.strip('>')
                                if 'www.youtube.com/watch?v=' in data or \
                                        'soundcloud.com' in data:
                                    self.player = (
                                        await self.voice.create_ytdl_player(
                                            data,
                                            ytdl_options=self.ytdlo,
                                            options=self.ffmop,
                                            after=self.voice_playlist))
                                    self._sent_finished_message = False
                                    self.is_bot_playing = True
                                    if self.player is not None:
                                        try:
                                            fulldir = self.player.duration
                                            minutes = str(
                                                int((fulldir / 60) % 60))
                                            seconds = str(int(fulldir % 60))
                                            if len(seconds) == 1:
                                                seconds = "0" + seconds
                                            try:
                                                message_data = str(
                                                    self.voice_text[
                                                        'play_command_data'][
                                                        1]).format(
                                                    str(self.player.title),
                                                    str(self.player.uploader),
                                                    minutes,
                                                    seconds)
                                                await self.bot.send_message(
                                                    self.voice_message_channel,
                                                    content=message_data)
                                            except discord.Forbidden:
                                                await self.rsme(self.bot, ctx)
                                            try:
                                                self.player.start()
                                            except RuntimeError:
                                                pass
                                        except AttributeError:
                                            message_data = str(
                                                self.voice_text[
                                                    'play_command_data'][2])
                                            self.is_bot_playing = False
                                            await self.bot.send_message(
                                                self.voice_message_channel,
                                                content=message_data)
                        except IndexError:
                            return
                        except discord.HTTPException:
                            message_data = str(
                                self.voice_text['play_command_data'][
                                    4]).format(str(sys.path))
                            await self.bot.send_message(ctx.message.channel,
                                                        content=message_data)
                            self.player = None
                        except youtube_dl.utils.UnsupportedError:
                            await self.bot.send_message(
                                ctx.message.channel, content=str(
                                    self.voice_text[
                                        'play_command_data'
                                    ][5]))
                            self.player = None
                        except youtube_dl.utils.ExtractorError:
                            message_data = str(
                                self.voice_text['play_command_data'][6])
                            await self.bot.send_message(ctx.message.channel,
                                                        content=message_data)
                            self.player = None
                        except youtube_dl.utils.DownloadError:
                            await self.bot.send_message(
                                ctx.message.channel, content=str(
                                    self.voice_text[
                                        'play_command_data'
                                    ][7]))
                            self.player = None
                    else:
                        return
            else:
                message_data = str(
                    self.voice_text['play_command_data'][8])
                await self.bot.send_message(ctx.message.channel,
                                            content=message_data)
        else:
            if self.player is not None:
                data = ctx.message.content[
                       len(ctx.prefix + "play "):].strip()
                if data == "":
                    try:
                        message_data = str(
                            self.voice_text['play_command_data'][9])
                        await self.bot.send_message(self.voice_message_channel,
                                                    content=message_data)
                    except discord.Forbidden:
                        await self.bot.BotPMError.resolve_send_message_error(
                            self.bot, ctx)
                else:
                    if '<' and '>' in data:
                        data = data.replace('<', '').replace('>', '')
                    if data.rfind('https://') == -1 and data.rfind(
                            'http://') == -1:
                        if len(self.bot_playlist) == 0:
                            self._temp_player_1 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist01 = self._temp_player_1.title
                                playlist01time = self._temp_player_1.duration
                                track1 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist01)
                                fulldir = playlist01time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track1time = newdir
                                track1uploader = str(
                                    self._temp_player_1.uploader)
                                track1info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track1,
                                                    track1uploader,
                                                    track1time)
                                self.bot_playlist_entries.append(track1info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track1, track1time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif data in self.bot_playlist:
                            msgdata = str(
                                self.voice_text['play_command_data'][14])
                            message_data = msgdata
                            await self.bot.send_message(ctx.message.channel,
                                                        content=message_data)
                        elif len(self.bot_playlist) == 1:
                            self._temp_player_2 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist02 = self._temp_player_2.title
                                playlist02time = self._temp_player_2.duration
                                track2 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist02)
                                fulldir = playlist02time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track2time = newdir
                                track2uploader = str(
                                    self._temp_player_2.uploader)
                                track2info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track2,
                                                    track2uploader,
                                                    track2time)
                                self.bot_playlist_entries.append(track2info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track2, track2time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 2:
                            self._temp_player_3 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist03 = self._temp_player_3.title
                                playlist03time = self._temp_player_3.duration
                                track3 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist03)
                                fulldir = playlist03time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track3time = newdir
                                track3uploader = str(
                                    self._temp_player_3.uploader)
                                track3info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track3,
                                                    track3uploader,
                                                    track3time)
                                self.bot_playlist_entries.append(track3info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track3, track3time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 3:
                            self._temp_player_4 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist04 = self._temp_player_4.title
                                playlist04time = self._temp_player_4.duration
                                track4 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist04)
                                fulldir = playlist04time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track4time = newdir
                                track4uploader = str(
                                    self._temp_player_4.uploader)
                                track4info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track4,
                                                    track4uploader,
                                                    track4time)
                                self.bot_playlist_entries.append(track4info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track4, track4time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 4:
                            self._temp_player_5 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist05 = self._temp_player_5.title
                                playlist05time = self._temp_player_5.duration
                                track5 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist05)
                                fulldir = playlist05time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track5time = newdir
                                track5uploader = str(
                                    self._temp_player_5.uploader)
                                track5info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track5,
                                                    track5uploader,
                                                    track5time)
                                self.bot_playlist_entries.append(track5info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track5, track5time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 5:
                            self._temp_player_6 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist06 = self._temp_player_6.title
                                playlist06time = self._temp_player_6.duration
                                track6 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist06)
                                fulldir = playlist06time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track6time = newdir
                                track6uploader = str(
                                    self._temp_player_6.uploader)
                                track6info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track6,
                                                    track6uploader,
                                                    track6time)
                                self.bot_playlist_entries.append(track6info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track6, track6time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 6:
                            self._temp_player_7 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist07 = self._temp_player_7.title
                                playlist07time = self._temp_player_7.duration
                                track7 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist07)
                                fulldir = playlist07time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track7time = newdir
                                track7uploader = str(
                                    self._temp_player_7.uploader)
                                track7info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track7,
                                                    track7uploader,
                                                    track7time)
                                self.bot_playlist_entries.append(track7info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track7, track7time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 7:
                            self._temp_player_8 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist08 = self._temp_player_8.title
                                playlist08time = self._temp_player_8.duration
                                track8 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist08)
                                fulldir = playlist08time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track8time = newdir
                                track8uploader = str(
                                    self._temp_player_8.uploader)
                                track8info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track8,
                                                    track8uploader,
                                                    track8time)
                                self.bot_playlist_entries.append(track8info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track8, track8time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 8:
                            self._temp_player_9 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist09 = self._temp_player_9.title
                                playlist09time = self._temp_player_9.duration
                                track9 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist09)
                                fulldir = playlist09time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track9time = newdir
                                track9uploader = str(
                                    self._temp_player_9.uploader)
                                track9info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track9,
                                                    track9uploader,
                                                    track9time)
                                self.bot_playlist_entries.append(track9info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track9, track9time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 9:
                            self._temp_player_10 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist10 = self._temp_player_10.title
                                playlist10time = self._temp_player_10.duration
                                track10 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist10)
                                fulldir = playlist10time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track10time = newdir
                                track10uploader = str(
                                    self._temp_player_10.uploader)
                                track10info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track10,
                                                    track10uploader,
                                                    track10time)
                                self.bot_playlist_entries.append(track10info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track10,
                                                    track10time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 10:
                            msgdata = str(
                                self.voice_text['play_command_data'][15])
                            message_data = msgdata
                            await self.bot.send_message(ctx.message.channel,
                                                        content=message_data)
                    if 'www.youtube.com/watch?v=' in data or \
                            'soundcloud.com' in data:
                        if len(self.bot_playlist) == 0:
                            self._temp_player_1 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist01 = self._temp_player_1.title
                                playlist01time = self._temp_player_1.duration
                                track1 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist01)
                                fulldir = playlist01time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track1time = newdir
                                track1uploader = str(
                                    self._temp_player_1.uploader)
                                track1info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track1,
                                                    track1uploader,
                                                    track1time)
                                self.bot_playlist_entries.append(track1info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track1, track1time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif data in self.bot_playlist:
                            msgdata = str(
                                self.voice_text['play_command_data'][14])
                            message_data = msgdata
                            await self.bot.send_message(ctx.message.channel,
                                                        content=message_data)
                        elif len(self.bot_playlist) == 1:
                            self._temp_player_2 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist02 = self._temp_player_2.title
                                playlist02time = self._temp_player_2.duration
                                track2 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist02)
                                fulldir = playlist02time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track2time = newdir
                                track2uploader = str(
                                    self._temp_player_2.uploader)
                                track2info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track2,
                                                    track2uploader,
                                                    track2time)
                                self.bot_playlist_entries.append(track2info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track2, track2time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 2:
                            self._temp_player_3 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist03 = self._temp_player_3.title
                                playlist03time = self._temp_player_3.duration
                                track3 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist03)
                                fulldir = playlist03time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track3time = newdir
                                track3uploader = str(
                                    self._temp_player_3.uploader)
                                track3info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track3,
                                                    track3uploader,
                                                    track3time)
                                self.bot_playlist_entries.append(track3info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track3, track3time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 3:
                            self._temp_player_4 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist04 = self._temp_player_4.title
                                playlist04time = self._temp_player_4.duration
                                track4 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist04)
                                fulldir = playlist04time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track4time = newdir
                                track4uploader = str(
                                    self._temp_player_4.uploader)
                                track4info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track4,
                                                    track4uploader,
                                                    track4time)
                                self.bot_playlist_entries.append(track4info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track4, track4time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 4:
                            self._temp_player_5 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist05 = self._temp_player_5.title
                                playlist05time = self._temp_player_5.duration
                                track5 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist05)
                                fulldir = playlist05time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track5time = newdir
                                track5uploader = str(
                                    self._temp_player_5.uploader)
                                track5info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track5,
                                                    track5uploader,
                                                    track5time)
                                self.bot_playlist_entries.append(track5info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track5, track5time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 5:
                            self._temp_player_6 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist06 = self._temp_player_6.title
                                playlist06time = self._temp_player_6.duration
                                track6 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist06)
                                fulldir = playlist06time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track6time = newdir
                                track6uploader = str(
                                    self._temp_player_6.uploader)
                                track6info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track6,
                                                    track6uploader,
                                                    track6time)
                                self.bot_playlist_entries.append(track6info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track6, track6time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 6:
                            self._temp_player_7 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist07 = self._temp_player_7.title
                                playlist07time = self._temp_player_7.duration
                                track7 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist07)
                                fulldir = playlist07time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track7time = newdir
                                track7uploader = str(
                                    self._temp_player_7.uploader)
                                track7info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track7,
                                                    track7uploader,
                                                    track7time)
                                self.bot_playlist_entries.append(track7info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track7, track7time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 7:
                            self._temp_player_8 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist08 = self._temp_player_8.title
                                playlist08time = self._temp_player_8.duration
                                track8 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist08)
                                fulldir = playlist08time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track8time = newdir
                                track8uploader = str(
                                    self._temp_player_8.uploader)
                                track8info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track8,
                                                    track8uploader,
                                                    track8time)
                                self.bot_playlist_entries.append(track8info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track8, track8time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 8:
                            self._temp_player_9 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist09 = self._temp_player_9.title
                                playlist09time = self._temp_player_9.duration
                                track9 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist09)
                                fulldir = playlist09time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track9time = newdir
                                track9uploader = str(
                                    self._temp_player_9.uploader)
                                track9info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track9,
                                                    track9uploader,
                                                    track9time)
                                self.bot_playlist_entries.append(track9info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track9, track9time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 9:
                            self._temp_player_10 = (
                                await self.voice.create_ytdl_player(
                                    data,
                                    ytdl_options=self.ytdlo,
                                    options=self.ffmop))
                            self.bot_playlist.append(data)
                            try:
                                playlist10 = self._temp_player_10.title
                                playlist10time = self._temp_player_10.duration
                                track10 = str(
                                    self.voice_text['play_command_data'][
                                        10]).format(playlist10)
                                fulldir = playlist10time
                                minutes = str(int((fulldir / 60) % 60))
                                seconds = str(int(fulldir % 60))
                                if len(seconds) == 1:
                                    seconds = "0" + seconds
                                newdir = str(
                                    self.voice_text['play_command_data'][
                                        11]).format(minutes, seconds)
                                track10time = newdir
                                track10uploader = str(
                                    self._temp_player_10.uploader)
                                track10info = str(
                                    self.voice_text['play_command_data'][
                                        12]).format(track10,
                                                    track10uploader,
                                                    track10time)
                                self.bot_playlist_entries.append(track10info)
                                msgdata = str(
                                    self.voice_text['play_command_data'][
                                        13]).format(track10,
                                                    track10time)
                                message_data = msgdata
                                await self.bot.send_message(
                                    ctx.message.channel, content=message_data)
                            except AttributeError:
                                message_data = str(
                                    self.voice_text['play_command_data'][
                                        2])
                                await self.bot.send_message(
                                    self.voice_message_channel,
                                    content=message_data)
                        elif len(self.bot_playlist) == 10:
                            msgdata = str(
                                self.voice_text['play_command_data'][15])
                            message_data = msgdata
                            await self.bot.send_message(ctx.message.channel,
                                                        content=message_data)

    # will be revised on next release of this cog!!!

    @commands.command(name='stop', pass_context=True, no_pm=True)
    async def stop_command(self, ctx):
        """
        Bot Voice Command.
        :param ctx: Command Context.
        """
        if ctx.message.channel.id in self.bot.ignoreslist["channels"]:
            return
        if ctx.message.author.id in self.bot.banlist['Users']:
            return
        elif self.voice_message_channel is not None:
            if ctx.message.channel.id == self.voice_message_channel.id:
                if self.player is not None:
                    fulldir = self.player.duration
                    minutes = str(int((fulldir / 60) % 60))
                    seconds = str(int(fulldir % 60))
                    if len(seconds) == 1:
                        seconds = "0" + seconds
                    try:
                        message_data = str(
                            self.voice_text['stop_command_data'][
                                0]).format(str(self.player.title),
                                           str(self.player.uploader
                                               ), minutes, seconds)
                        await self.bot.send_message(self.voice_message_channel,
                                                    content=message_data)
                    except discord.Forbidden:
                        await self.bot.BotPMError.resolve_send_message_error(
                            self.bot, ctx)
                    self.player.stop()
                    self.player = None
                    self.is_bot_playing = False
                    # Clean the temp players now...
                    self.resolve_bot_playlist_issue()
                    if len(self.bot_playlist) >= 1:
                        try:
                            track_data = None
                            try:
                                track_data = str(self.bot_playlist_entries[0])
                            except IndexError:
                                pass
                            data = str(self.bot_playlist[0])
                            self._sent_finished_message = False
                            self.player = await self.voice.create_ytdl_player(
                                data, ytdl_options=self.ytdlo,
                                options=self.ffmop, after=self.voice_playlist)
                            if self.player is not None:
                                try:
                                    self.bot_playlist.remove(data)
                                    self.bot_playlist_entries.remove(
                                        track_data)
                                except ValueError:
                                    pass
                                if self.is_bot_playing is False:
                                    self.is_bot_playing = True
                                    try:
                                        fulldir = self.player.duration
                                        minutes = str(int((fulldir / 60) % 60))
                                        seconds = str(int(fulldir % 60))
                                        if len(seconds) == 1:
                                            seconds = "0" + seconds
                                        track_info = str(
                                            self.voice_text[
                                                'stop_command_data'
                                            ][1]).format(
                                            str(self.player.title),
                                            str(self.player.uploader))
                                        message_data = str(
                                            self.voice_text[
                                                'stop_command_data'][
                                                2]).format(
                                            track_info, minutes, seconds)
                                        await self.bot.send_message(
                                            self.voice_message_channel,
                                            content=message_data)
                                        try:
                                            self.bot_playlist_entries.remove(
                                                track_info)
                                        except ValueError:
                                            pass
                                    except discord.Forbidden:
                                        await self.resolve_send_message_error(
                                            self.bot, ctx)
                                    if self.player is not None:
                                        self.player.start()
                        except UnboundLocalError:
                            self.player = None
                            self.is_bot_playing = False
                else:
                    try:
                        message_data = str(
                            self.voice_text['stop_command_data'][3])
                        await self.bot.send_message(self.voice_message_channel,
                                                    content=message_data)
                    except discord.Forbidden:
                        await self.bot.BotPMError.resolve_send_message_error(
                            self.bot, ctx)
            else:
                return

    # will be revised on next release of this cog!!!

    @commands.command(name='pause', pass_context=True, no_pm=True)
    async def pause_command(self, ctx):
        """
        Bot Voice Command.
        :param ctx: Command Context.
        """
        if ctx.message.channel.id in self.bot.ignoreslist["channels"]:
            return
        if ctx.message.author.id in self.bot.banlist['Users']:
            return
        elif self.voice_message_channel is not None:
            if ctx.message.channel.id == self.voice_message_channel.id:
                if self.player is not None:
                    fulldir = self.player.duration
                    minutes = str(int((fulldir / 60) % 60))
                    seconds = str(int(fulldir % 60))
                    if len(seconds) == 1:
                        seconds = "0" + seconds
                    try:
                        message_data = str(
                            self.voice_text['pause_command_data'][
                                0]).format(
                            str(self.player.title), str(self.player.uploader),
                            minutes, seconds)
                        await self.bot.send_message(self.voice_message_channel,
                                                    content=message_data)
                    except discord.Forbidden:
                        await self.bot.BotPMError.resolve_send_message_error(
                            self.bot, ctx)
                    self.player.pause()
                else:
                    message_data = str(
                        self.voice_text['pause_command_data'][1])
                    await self.bot.send_message(self.voice_message_channel,
                                                content=message_data)
            else:
                return
        else:
            message_data = str(self.voice_text['pause_command_data'][2])
            await self.bot.send_message(ctx.message.channel,
                                        content=message_data)

    # will be revised on next release of this cog!!!

    @commands.command(name='unpause', pass_context=True, no_pm=True)
    async def unpause_command(self, ctx):
        """
        Bot Voice Command.
        :param ctx: Command Context.
        """
        if ctx.message.channel.id in self.bot.ignoreslist["channels"]:
            return
        if ctx.message.author.id in self.bot.banlist['Users']:
            return
        elif self.voice_message_channel is not None:
            if ctx.message.channel.id == self.voice_message_channel.id:
                if self.player is not None:
                    fulldir = self.player.duration
                    minutes = str(int((fulldir / 60) % 60))
                    seconds = str(int(fulldir % 60))
                    if len(seconds) == 1:
                        seconds = "0" + seconds
                    try:
                        message_data = str(
                            self.voice_text['unpause_command_data'][
                                0]).format(
                            str(self.player.title), str(self.player.uploader),
                            minutes, seconds)
                        await self.bot.send_message(self.voice_message_channel,
                                                    content=message_data)
                    except discord.Forbidden:
                        await self.bot.BotPMError.resolve_send_message_error(
                            self.bot, ctx)
                    self.player.resume()
                else:
                    try:
                        msgdata = str(
                            self.voice_text['unpause_command_data'][1])
                        message_data = msgdata
                        await self.bot.send_message(self.voice_message_channel,
                                                    content=message_data)
                    except discord.Forbidden:
                        await self.bot.BotPMError.resolve_send_message_error(
                            self.bot, ctx)
            else:
                return
        else:
            message_data = str(self.voice_text['unpause_command_data'][2])
            await self.bot.send_message(ctx.message.channel,
                                        content=message_data)

    # will be revised on next release of this cog!!!

    @commands.command(name='move', pass_context=True, no_pm=True)
    async def move_command(self, ctx):
        """
        Bot Voice Command.
        :param ctx: Command Context.
        """
        if ctx.message.channel.id in self.bot.ignoreslist["channels"]:
            return
        if ctx.message.author.id in self.bot.banlist['Users']:
            return
        elif self.voice_message_channel is not None:
            if ctx.message.channel.id == self.voice_message_channel.id:
                if ctx.message.author.voice_channel != \
                        ctx.message.channel.server.me.voice_channel:
                    self.botvoicechannel['Bot_Current_Voice_Channel'].remove(
                        self.vchannel.id)
                    self.botvoicechannel['Bot_Current_Voice_Channel'].remove(
                        self.voice_message_server.id)
                    self.botvoicechannel['Bot_Current_Voice_Channel'].remove(
                        self.voice_message_channel.id)
                    self.botvoicechannel['Bot_Current_Voice_Channel'].remove(
                        self.voice_message_server_name)
                    self.botvoicechannel['Bot_Current_Voice_Channel'].remove(
                        self.vchannel_name)
                    self.vchannel = ctx.message.author.voice_channel
                    self.vchannel_name = ctx.message.author.voice_channel.name
                    if self.vchannel.id not in self.botvoicechannel:
                        self.botvoicechannel[
                            'Bot_Current_Voice_Channel'].append(
                            self.vchannel.id)
                    if self.voice_message_server.id not in \
                            self.botvoicechannel:
                        self.botvoicechannel[
                            'Bot_Current_Voice_Channel'].append(
                            self.voice_message_server.id)
                    if self.voice_message_channel.id not in \
                            self.botvoicechannel:
                        self.botvoicechannel[
                            'Bot_Current_Voice_Channel'].append(
                            self.voice_message_channel.id)
                    if self.voice_message_server_name not in \
                            self.botvoicechannel:
                        self.botvoicechannel[
                            'Bot_Current_Voice_Channel'].append(
                            self.voice_message_server_name)
                    if self.vchannel_name not in self.botvoicechannel:
                        self.botvoicechannel[
                            'Bot_Current_Voice_Channel'].append(
                            self.vchannel_name)
                    file_name = os.path.join(
                        sys.path[0], 'resources', 'ConfigData',
                        'BotVoiceChannel.json')
                    json.dump(self.botvoicechannel, open(file_name, "w"))
                    try:
                        await self.voice.move_to(self.vchannel)
                        try:
                            message_data = str(
                                self.voice_text['move_command_data'][
                                    0]).format(self.vchannel.name)
                            await self.bot.send_message(
                                self.voice_message_channel,
                                content=message_data)
                        except discord.Forbidden:
                            await self.resolve_send_message_error(
                                self.bot, ctx)
                    except discord.InvalidArgument:
                        try:
                            message_data = str(
                                self.voice_text['move_command_data'][1])
                            await self.bot.send_message(
                                self.voice_message_channel,
                                content=message_data)
                        except discord.Forbidden:
                            await self.resolve_send_message_error(
                                self.bot, ctx)
                else:
                    message_data = str(
                        self.voice_text['move_command_data'][2])
                    await self.bot.send_message(self.voice_message_channel,
                                                content=message_data)
            else:
                return

    # will be revised on next release of this cog!!!

    @commands.command(name='LeaveVoiceChannel', pass_context=True, no_pm=True)
    async def leave_voice_channel_command(self, ctx):
        """
        Bot Voice Command.
        :param ctx: Command Context.
        """
        if ctx.message.channel.id in self.bot.ignoreslist["channels"]:
            return
        if ctx.message.author.id in self.bot.banlist['Users']:
            return
        elif self.voice is not None:
            if self.voice_message_channel is not None:
                if ctx.message.channel.id == self.voice_message_channel.id:
                    try:
                        await self.voice.disconnect()
                    except ConnectionResetError:
                        # Supress a Error here.
                        pass
                    if self.vchannel is not None:
                        try:
                            self.botvoicechannel[
                                'Bot_Current_Voice_Channel'].remove(
                                self.vchannel.id)
                        except ValueError:
                            pass
                        try:
                            self.botvoicechannel[
                                'Bot_Current_Voice_Channel'].remove(
                                self.voice_message_server.id)
                        except ValueError:
                            pass
                        try:
                            self.botvoicechannel[
                                'Bot_Current_Voice_Channel'].remove(
                                self.voice_message_channel.id)
                        except ValueError:
                            pass
                        try:
                            self.botvoicechannel[
                                'Bot_Current_Voice_Channel'].remove(
                                self.voice_message_server_name)
                        except ValueError:
                            pass
                        try:
                            self.botvoicechannel[
                                'Bot_Current_Voice_Channel'].remove(
                                self.vchannel_name)
                        except ValueError:
                            pass
                    filename = os.path.join(
                        sys.path[0], 'resources', 'ConfigData',
                        'BotVoiceChannel.json')
                    json.dump(self.botvoicechannel, open(filename, "w"))
                    try:
                        try:
                            message_data = str(
                                self.voice_text[
                                    'leave_voice_channel_command_data'
                                ][0]).format(self.vchannel.name)
                        except AttributeError:
                            message_data = str(
                                self.voice_text[
                                    'leave_voice_channel_command_data'
                                ][0]).format(self.vchannel_name)
                        await self.bot.send_message(self.voice_message_channel,
                                                    content=message_data)
                    except discord.Forbidden:
                        await self.bot.BotPMError.resolve_send_message_error(
                            self.bot, ctx)
                    self.vchannel = None
                    self.voice_message_channel = None
                    self.voice = None
                    self.vchannel_name = None
                    if self.player is not None:
                        self.player = None
                    self.voice_message_server = None
                    if self.is_bot_playing:
                        self.is_bot_playing = False
                else:
                    return
        else:
            msgdata = str(
                self.voice_text['leave_voice_channel_command_data'][1])
            message_data = msgdata
            await self.bot.send_message(ctx.message.channel, message_data)

    # will be revised on next release of this cog!!!

    @commands.command(name='Playlist', pass_context=True, no_pm=True)
    async def playlist_command(self, ctx):
        """
        Bot Voice Command.
        :param ctx: Command Context.
        """
        if ctx.message.channel.id in self.bot.ignoreslist["channels"]:
            return
        if ctx.message.author.id in self.bot.banlist['Users']:
            return
        elif self.voice is not None:
            if self.voice_message_channel is not None:
                if ctx.message.channel.id == self.voice_message_channel.id:
                    track1 = str(
                        self.voice_text['playlist_command_data'][0])
                    track2 = str(
                        self.voice_text['playlist_command_data'][0])
                    track3 = str(
                        self.voice_text['playlist_command_data'][0])
                    track4 = str(
                        self.voice_text['playlist_command_data'][0])
                    track5 = str(
                        self.voice_text['playlist_command_data'][0])
                    track6 = str(
                        self.voice_text['playlist_command_data'][0])
                    track7 = str(
                        self.voice_text['playlist_command_data'][0])
                    track8 = str(
                        self.voice_text['playlist_command_data'][0])
                    track9 = str(
                        self.voice_text['playlist_command_data'][0])
                    track10 = str(
                        self.voice_text['playlist_command_data'][0])
                    if len(self.bot_playlist_entries) == 0:
                        track1 = str(
                            self.voice_text['playlist_command_data'][0])
                        track2 = str(
                            self.voice_text['playlist_command_data'][0])
                        track3 = str(
                            self.voice_text['playlist_command_data'][0])
                        track4 = str(
                            self.voice_text['playlist_command_data'][0])
                        track5 = str(
                            self.voice_text['playlist_command_data'][0])
                        track6 = str(
                            self.voice_text['playlist_command_data'][0])
                        track7 = str(
                            self.voice_text['playlist_command_data'][0])
                        track8 = str(
                            self.voice_text['playlist_command_data'][0])
                        track9 = str(
                            self.voice_text['playlist_command_data'][0])
                        track10 = str(
                            self.voice_text['playlist_command_data'][0])
                    elif len(self.bot_playlist_entries) == 1:
                        track1 = str(self.bot_playlist_entries[0])
                        track2 = str(
                            self.voice_text['playlist_command_data'][0])
                        track3 = str(
                            self.voice_text['playlist_command_data'][0])
                        track4 = str(
                            self.voice_text['playlist_command_data'][0])
                        track5 = str(
                            self.voice_text['playlist_command_data'][0])
                        track6 = str(
                            self.voice_text['playlist_command_data'][0])
                        track7 = str(
                            self.voice_text['playlist_command_data'][0])
                        track8 = str(
                            self.voice_text['playlist_command_data'][0])
                        track9 = str(
                            self.voice_text['playlist_command_data'][0])
                        track10 = str(
                            self.voice_text['playlist_command_data'][0])
                    elif len(self.bot_playlist_entries) == 2:
                        track1 = str(self.bot_playlist_entries[0])
                        track2 = str(self.bot_playlist_entries[1])
                        track3 = str(
                            self.voice_text['playlist_command_data'][0])
                        track4 = str(
                            self.voice_text['playlist_command_data'][0])
                        track5 = str(
                            self.voice_text['playlist_command_data'][0])
                        track6 = str(
                            self.voice_text['playlist_command_data'][0])
                        track7 = str(
                            self.voice_text['playlist_command_data'][0])
                        track8 = str(
                            self.voice_text['playlist_command_data'][0])
                        track9 = str(
                            self.voice_text['playlist_command_data'][0])
                        track10 = str(
                            self.voice_text['playlist_command_data'][0])
                    elif len(self.bot_playlist_entries) == 3:
                        track1 = str(self.bot_playlist_entries[0])
                        track2 = str(self.bot_playlist_entries[1])
                        track3 = str(self.bot_playlist_entries[2])
                        track4 = str(
                            self.voice_text['playlist_command_data'][0])
                        track5 = str(
                            self.voice_text['playlist_command_data'][0])
                        track6 = str(
                            self.voice_text['playlist_command_data'][0])
                        track7 = str(
                            self.voice_text['playlist_command_data'][0])
                        track8 = str(
                            self.voice_text['playlist_command_data'][0])
                        track9 = str(
                            self.voice_text['playlist_command_data'][0])
                        track10 = str(
                            self.voice_text['playlist_command_data'][0])
                    elif len(self.bot_playlist_entries) == 4:
                        track1 = str(self.bot_playlist_entries[0])
                        track2 = str(self.bot_playlist_entries[1])
                        track3 = str(self.bot_playlist_entries[2])
                        track4 = str(self.bot_playlist_entries[3])
                        track5 = str(
                            self.voice_text['playlist_command_data'][0])
                        track6 = str(
                            self.voice_text['playlist_command_data'][0])
                        track7 = str(
                            self.voice_text['playlist_command_data'][0])
                        track8 = str(
                            self.voice_text['playlist_command_data'][0])
                        track9 = str(
                            self.voice_text['playlist_command_data'][0])
                        track10 = str(
                            self.voice_text['playlist_command_data'][0])
                    elif len(self.bot_playlist_entries) == 5:
                        track1 = str(self.bot_playlist_entries[0])
                        track2 = str(self.bot_playlist_entries[1])
                        track3 = str(self.bot_playlist_entries[2])
                        track4 = str(self.bot_playlist_entries[3])
                        track5 = str(self.bot_playlist_entries[4])
                        track6 = str(
                            self.voice_text['playlist_command_data'][0])
                        track7 = str(
                            self.voice_text['playlist_command_data'][0])
                        track8 = str(
                            self.voice_text['playlist_command_data'][0])
                        track9 = str(
                            self.voice_text['playlist_command_data'][0])
                        track10 = str(
                            self.voice_text['playlist_command_data'][0])
                    elif len(self.bot_playlist_entries) == 6:
                        track1 = str(self.bot_playlist_entries[0])
                        track2 = str(self.bot_playlist_entries[1])
                        track3 = str(self.bot_playlist_entries[2])
                        track4 = str(self.bot_playlist_entries[3])
                        track5 = str(self.bot_playlist_entries[4])
                        track6 = str(self.bot_playlist_entries[5])
                        track7 = str(
                            self.voice_text['playlist_command_data'][0])
                        track8 = str(
                            self.voice_text['playlist_command_data'][0])
                        track9 = str(
                            self.voice_text['playlist_command_data'][0])
                        track10 = str(
                            self.voice_text['playlist_command_data'][0])
                    elif len(self.bot_playlist_entries) == 7:
                        track1 = str(self.bot_playlist_entries[0])
                        track2 = str(self.bot_playlist_entries[1])
                        track3 = str(self.bot_playlist_entries[2])
                        track4 = str(self.bot_playlist_entries[3])
                        track5 = str(self.bot_playlist_entries[4])
                        track6 = str(self.bot_playlist_entries[5])
                        track7 = str(self.bot_playlist_entries[6])
                        track8 = str(
                            self.voice_text['playlist_command_data'][0])
                        track9 = str(
                            self.voice_text['playlist_command_data'][0])
                        track10 = str(
                            self.voice_text['playlist_command_data'][0])
                    elif len(self.bot_playlist_entries) == 8:
                        track1 = str(self.bot_playlist_entries[0])
                        track2 = str(self.bot_playlist_entries[1])
                        track3 = str(self.bot_playlist_entries[2])
                        track4 = str(self.bot_playlist_entries[3])
                        track5 = str(self.bot_playlist_entries[4])
                        track6 = str(self.bot_playlist_entries[5])
                        track7 = str(self.bot_playlist_entries[6])
                        track8 = str(self.bot_playlist_entries[7])
                        track9 = str(
                            self.voice_text['playlist_command_data'][0])
                        track10 = str(
                            self.voice_text['playlist_command_data'][0])
                    elif len(self.bot_playlist_entries) == 9:
                        track1 = str(self.bot_playlist_entries[0])
                        track2 = str(self.bot_playlist_entries[1])
                        track3 = str(self.bot_playlist_entries[2])
                        track4 = str(self.bot_playlist_entries[3])
                        track5 = str(self.bot_playlist_entries[4])
                        track6 = str(self.bot_playlist_entries[5])
                        track7 = str(self.bot_playlist_entries[6])
                        track8 = str(self.bot_playlist_entries[7])
                        track9 = str(self.bot_playlist_entries[8])
                        track10 = str(
                            self.voice_text['playlist_command_data'][0])
                    elif len(self.bot_playlist_entries) == 10:
                        track1 = str(self.bot_playlist_entries[0])
                        track2 = str(self.bot_playlist_entries[1])
                        track3 = str(self.bot_playlist_entries[2])
                        track4 = str(self.bot_playlist_entries[3])
                        track5 = str(self.bot_playlist_entries[4])
                        track6 = str(self.bot_playlist_entries[5])
                        track7 = str(self.bot_playlist_entries[6])
                        track8 = str(self.bot_playlist_entries[7])
                        track9 = str(self.bot_playlist_entries[8])
                        track10 = str(self.bot_playlist_entries[9])
                    msgdata = str(
                        self.voice_text['playlist_command_data'][
                            1]).format(track1, track2, track3,
                                       track4, track5, track6,
                                       track7, track8, track9,
                                       track10)
                    message_data = msgdata
                    await self.bot.send_message(ctx.message.channel,
                                                content=message_data)

    # will be revised on next release of this cog!!!

    @commands.command(name='vol', pass_context=True, no_pm=True)
    async def vol_command(self, ctx):
        """
        Bot Voice Command.
        :param ctx: Command Context.
        """
        if ctx.message.channel.id in self.bot.ignoreslist["channels"]:
            return
        if ctx.message.author.id in self.bot.banlist['Users']:
            return
        elif self.voice_message_channel is not None:
            if ctx.message.channel.id == self.voice_message_channel.id:
                if self.player is not None:
                    value_string = ctx.message.content.strip(
                        ctx.prefix + "vol ")
                    try:
                        value = float(value_string) / 100
                        if 0.0 <= value <= 2.0:
                            self.player.volume = value
                            value_message = str(
                                self.voice_text['volume_command_data'][
                                    0]).format(str(value * 100))
                            await self.bot.send_message(
                                self.voice_message_channel,
                                content=value_message)
                        else:
                            await self.bot.send_message(
                                self.voice_message_channel,
                                content=str(
                                    self.voice_text[
                                        'volume_command_data'][1]))
                    except ValueError:
                        await self.bot.send_message(
                            self.voice_message_channel, content=str(
                                self.voice_text[
                                    'volume_command_data'
                                ][2]))
            else:
                await self.bot.send_message(
                    self.voice_message_channel, content=str(
                        self.voice_text[
                            'volume_command_data'
                        ][3]))

    def voice_playlist(self):
        """
        Listens for when music stops playing.
        """
        discord.compat.run_coroutine_threadsafe(self.playlist_iterator(),
                                                loop=self.bot.loop)

    # will be revised on next release of this cog!!!

    async def playlist_iterator(self):
        """
        Bot's Playlist Iterator.
        """
        if self.player.error is None:
            if self.voice_message_channel is not None:
                fulldir = self.player.duration
                minutes = str(int((fulldir / 60) % 60))
                seconds = str(int(fulldir % 60))
                if len(seconds) == 1:
                    seconds = "0" + seconds
                if self._sent_finished_message is False:
                    self._sent_finished_message = True
                    self.is_bot_playing = False
                    # Clean the temp players now...
                    self.resolve_bot_playlist_issue()
                    try:
                        message_data = str(
                            self.voice_text['auto_playlist_data'][
                                0]).format(
                            str(self.player.title), str(self.player.uploader),
                            minutes, seconds)
                        await self.bot.send_message(self.voice_message_channel,
                                                    content=message_data)
                    except discord.Forbidden:
                        pass
                if len(self.bot_playlist) == 0:
                    self.player = None
                if len(self.bot_playlist) >= 1:
                    try:
                        track_data = None
                        try:
                            track_data = str(self.bot_playlist_entries[0])
                        except IndexError:
                            pass
                        data = str(self.bot_playlist[0])
                        self._sent_finished_message = False
                        try:
                            self.player = await self.voice.create_ytdl_player(
                                data, ytdl_options=self.ytdlo,
                                options=self.ffmop, after=self.voice_playlist)
                        except AttributeError:
                            self.is_bot_playing = False
                        if self.player is not None:
                            try:
                                self.bot_playlist.remove(data)
                            except ValueError:
                                pass
                            try:
                                self.bot_playlist_entries.remove(track_data)
                            except ValueError:
                                pass
                            if self.is_bot_playing is False:
                                self.is_bot_playing = True
                                try:
                                    fulldir = self.player.duration
                                    minutes = str(int((fulldir / 60) % 60))
                                    seconds = str(int(fulldir % 60))
                                    if len(seconds) == 1:
                                        seconds = "0" + seconds
                                    track_info = str(self.voice_text[
                                                         'auto_playlist_data'][
                                                         1]).format(
                                        str(self.player.title),
                                        str(self.player.uploader))
                                    message_data = str(
                                        self.voice_text[
                                            'auto_playlist_data'
                                        ][2]).format(track_info, minutes,
                                                     seconds)
                                    await self.bot.send_message(
                                        self.voice_message_channel,
                                        content=message_data)
                                    try:
                                        self.bot_playlist_entries.remove(
                                            track_info)
                                    except ValueError:
                                        pass
                                except discord.Forbidden:
                                    pass
                                if self.player is not None:
                                    self.player.start()
                    except UnboundLocalError:
                        self.is_bot_playing = False
        else:
            if self.voice_message_channel is not None:
                await self.bot.send_message(
                    self.voice_message_channel,
                    content="A Error Occured while playing. {0}".format(
                        self.player.error))


def setup(bot):
    """
    DecoraterBot's Voice Channel Plugin.
    """
    cog = Voice(bot)
    cog.setup()
    bot.add_cog(cog)
