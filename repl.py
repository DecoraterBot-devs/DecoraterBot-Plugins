# coding=utf-8
"""
repl Plugin for DecoraterBot.
"""

import traceback
import inspect
from contextlib import redirect_stdout
import io

import discord
from discord.ext import commands
from DecoraterBotUtils.utils import *


class REPL:
    """
    repl Plugin class.
    """
    def __init__(self):
        self.sessions = set()
        self.repl_text = PluginTextReader(
            file='repl.json')

    @staticmethod
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @staticmethod
    def get_syntax_error(e):
        """Gets SyntaxErrors."""
        return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(
            e, '^', type(e).__name__)

    @commands.command(pass_context=True, hidden=True)
    async def repl(self, ctx):
        """adds / removes a repl session."""
        if ctx.message.author.id != ctx.bot.BotConfig.discord_user_id:
            return
        code = None
        msg = ctx.message

        variables = {
            'ctx': ctx,
            'bot': ctx.bot,
            'message': msg,
            'server': msg.server,
            'channel': msg.channel,
            'author': msg.author,
            'last': None,
        }

        if msg.channel.id in self.sessions:
            await ctx.bot.say(self.repl_text['repl_plugin_data'][0])
            return

        self.sessions.add(msg.channel.id)
        await ctx.bot.say(self.repl_text['repl_plugin_data'][1])
        while True:
            response = await ctx.bot.wait_for_message(
                author=msg.author, channel=msg.channel,
                check=lambda m: m.content.startswith('`'))

            cleaned = self.cleanup_code(response.content)

            if cleaned in ('quit', 'exit', 'exit()'):
                await ctx.bot.say(self.repl_text['repl_plugin_data'][2])
                self.sessions.remove(msg.channel.id)
                return

            executor = exec
            if cleaned.count('\n') == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    await ctx.bot.say(self.get_syntax_error(e))
                    continue

            variables['message'] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                str(e)  # to shut PyCharm up.
                value = stdout.getvalue()
                fmt = '{}{}\n'.format(value, traceback.format_exc())
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = '{}{}\n'.format(value, result)
                    variables['last'] = result
                elif value:
                    fmt = '{}\n'.format(value)

            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        for i in range(0, len(fmt), 1990):
                            await ctx.bot.send_message(msg.channel,
                                                        '```py\n{}```'.format(
                                                            fmt[i:i+1990]))
                    else:
                        await ctx.bot.send_message(msg.channel,
                                                    '```py\n{}```'.format(fmt))
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                await ctx.bot.send_message(msg.channel,
                                            (self.repl_text[
                                            'repl_plugin_data'][3]).format(e))


def setup(bot):
    """Adds plugin commands."""
    bot.add_cog(REPL())
