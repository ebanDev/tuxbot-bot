# Created by romain at 04/01/2020

import logging
import os
import pathlib
import platform
import re
import socket
import time
from socket import AF_INET6

import aiohttp
import discord
import humanize
import psutil
from discord.ext import commands
from tcp_latency import measure_latency

from bot import TuxBot
from utils import Texts
from utils import commandExtra

log = logging.getLogger(__name__)


class Useful(commands.Cog):

    def __init__(self, bot: TuxBot):
        self.bot = bot
        self.icon = ":toolbox:"
        self.big_icon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/233/toolbox_1f9f0.png"

    @staticmethod
    def _latest_commits():
        cmd = 'git log -n 3 -s --format="[\`%h\`](https://git.gnous.eu/gnouseu/tuxbot-bot/commits/%H) %s (%cr)"'

        return os.popen(cmd).read().strip()

    ###########################################################################

    @commandExtra(name='iplocalise', category='utility',
                  description=Texts('commands').get('utility._iplocalise'))
    async def _iplocalise(self, ctx: commands.Context, addr, ip_type=''):
        addr = re.sub(r'http(s?)://', '', addr)
        addr = addr[:-1] if addr.endswith('/') else addr

        await ctx.trigger_typing()

        try:
            if ip_type in ('v6', 'ipv6'):
                try:
                    ip = socket.getaddrinfo(addr, None, AF_INET6)[1][4][0]
                except socket.gaierror:
                    return await ctx.send(
                        Texts('utility', ctx).get('ipv6 not available'))
            else:
                ip = socket.gethostbyname(addr)

            async with self.bot.session.get(f"http://ip-api.com/json/{ip}") \
                    as s:
                response: dict = await s.json()

                if response.get('status') == 'success':
                    e = discord.Embed(
                        title=f"{Texts('utility', ctx).get('Information for')}"
                              f" ``{addr}`` *`({response.get('query')})`*",
                        color=0x5858d7
                    )

                    e.add_field(
                        name=Texts('utility', ctx).get('Belongs to :'),
                        value=response.get('org', 'N/A'),
                        inline=False
                    )

                    e.add_field(
                        name=Texts('utility', ctx).get('Is located at :'),
                        value=response.get('city', 'N/A'),
                        inline=True
                    )

                    e.add_field(
                        name="Region :",
                        value=f"{response.get('regionName', 'N/A')} "
                              f"({response.get('country', 'N/A')})",
                        inline=True
                    )

                    e.set_thumbnail(
                        url=f"https://www.countryflags.io/"
                            f"{response.get('countryCode')}/flat/64.png")

                    await ctx.send(embed=e)
                else:
                    await ctx.send(
                        content=f"{Texts('utility', ctx).get('info not available')}"
                                f"``{response.get('query')}``")

        except Exception:
            await ctx.send(
                f"{Texts('utility', ctx).get('Cannot connect to host')} {addr}"
            )

    ###########################################################################

    @commandExtra(name='getheaders', category='utility',
                  description=Texts('commands').get('utility._getheaders'))
    async def _getheaders(self, ctx: commands.Context, addr: str):
        if (addr.startswith('http') or addr.startswith('ftp')) is not True:
            addr = f"http://{addr}"

        await ctx.trigger_typing()

        try:
            async with self.bot.session.get(addr) as s:
                e = discord.Embed(
                    title=f"{Texts('utility', ctx).get('Headers of')} {addr}",
                    color=0xd75858
                )
                e.add_field(name="Status", value=s.status, inline=True)
                e.set_thumbnail(url=f"https://http.cat/{s.status}")

                headers = dict(s.headers.items())
                headers.pop('Set-Cookie', headers)

                for key, value in headers.items():
                    e.add_field(name=key, value=value, inline=True)
                await ctx.send(embed=e)

        except aiohttp.client_exceptions.ClientError:
            await ctx.send(
                f"{Texts('utility', ctx).get('Cannot connect to host')} {addr}"
            )

    ###########################################################################

    @commandExtra(name='git', aliases=['sources', 'source', 'github'],
                  category='utility',
                  description=Texts('commands').get('utility._git'))
    async def _git(self, ctx):
        e = discord.Embed(
            title=Texts('utility', ctx).get('git repo'),
            description=Texts('utility', ctx).get('git text'),
            colour=0xE9D460
        )
        e.set_author(
            name='Gnous',
            icon_url="https://cdn.gnous.eu/logo1.png"
        )
        await ctx.send(embed=e)

    ###########################################################################

    @commandExtra(name='quote', category='utility',
                  description=Texts('commands').get('utility._quote'))
    async def _quote(self, ctx, message_id: discord.Message):
        e = discord.Embed(
            colour=message_id.author.colour,
            description=message_id.clean_content,
            timestamp=message_id.created_at
        )
        e.set_author(
            name=message_id.author.display_name,
            icon_url=message_id.author.avatar_url_as(format="jpg")
        )
        if len(message_id.attachments) >= 1:
            e.set_image(url=message_id.attachments[0].url)

        e.add_field(name="**Original**",
                    value=f"[Go!]({message_id.jump_url})")
        e.set_footer(text="#" + message_id.channel.name)

        await ctx.send(embed=e)

    ###########################################################################

    @commandExtra(name='ping', category='basics',
                  description=Texts('commands').get('basics._ping'))
    async def _ping(self, ctx: commands.Context):
        start = time.perf_counter()
        await ctx.trigger_typing()
        end = time.perf_counter()

        latency = round(self.bot.latency * 1000, 2)
        typing = round((end - start) * 1000, 2)
        discordapp = measure_latency(host='google.com', wait=0)[0]

        e = discord.Embed(title='Ping', color=discord.Color.teal())
        e.add_field(name='Websocket', value=f'{latency}ms')
        e.add_field(name='Typing', value=f'{typing}ms')
        e.add_field(name='discordapp.com', value=f'{discordapp}ms')
        await ctx.send(embed=e)

    ###########################################################################

    @staticmethod
    def fetch_info():
        total = 0
        file_amount = 0
        ENV = "env"

        for path, _, files in os.walk("."):
            for name in files:
                file_dir = str(pathlib.PurePath(path, name))
                if not name.endswith(".py") or ENV in file_dir:
                    continue
                file_amount += 1
                with open(file_dir, "r", encoding="utf-8") as file:
                    for line in file:
                        if not line.strip().startswith("#") \
                                or not line.strip():
                            total += 1

        return total, file_amount

    @commandExtra(name='info', aliases=['about'], category='basics',
                  description=Texts('commands').get('basics._info'))
    async def _info(self, ctx: commands.Context):
        proc = psutil.Process()
        lines, files = self.fetch_info()

        with proc.oneshot():
            mem = proc.memory_full_info()
            e = discord.Embed(
                title=Texts('basics', ctx).get('Information about TuxBot'),
                color=0x89C4F9)

            e.add_field(
                name=f"__{Texts('basics', ctx).get('Latest changes')}__",
                value=self._latest_commits(),
                inline=False)

            e.add_field(
                name=f"__:busts_in_silhouette: "
                     f"{Texts('basics', ctx).get('Development')}__",
                value=f"**Romain#5117:** [git](https://git.gnous.eu/Romain)\n"
                      f"**Outout#4039:** [git](https://git.gnous.eu/mael)\n",
                inline=True
            )
            e.add_field(
                name="__<:python:596577462335307777> Python__",
                value=f"**python** `{platform.python_version()}`\n"
                      f"**discord.py** `{discord.__version__}`",
                inline=True
            )
            e.add_field(
                name="__:gear: Usage__",
                value=f"**{humanize.naturalsize(mem.rss)}** "
                      f"{Texts('basics', ctx).get('physical memory')}\n"
                      f"**{humanize.naturalsize(mem.vms)}** "
                      f"{Texts('basics', ctx).get('virtual memory')}\n",
                inline=True
            )

            e.add_field(
                name=f"__{Texts('basics', ctx).get('Servers count')}__",
                value=str(len(self.bot.guilds)),
                inline=True
            )
            e.add_field(
                name=f"__{Texts('basics', ctx).get('Channels count')}__",
                value=str(len([_ for _ in self.bot.get_all_channels()])),
                inline=True
            )
            e.add_field(
                name=f"__{Texts('basics', ctx).get('Members count')}__",
                value=str(len([_ for _ in self.bot.get_all_members()])),
                inline=True
            )

            e.add_field(
                name=f"__:file_folder: {Texts('basics', ctx).get('Files')}__",
                value=str(files),
                inline=True
            )
            e.add_field(
                name=f"__¶ {Texts('basics', ctx).get('Lines')}__",
                value=str(lines),
                inline=True
            )

            e.add_field(
                name=f"__:link: {Texts('basics', ctx).get('Links')}__",
                value="[tuxbot.gnous.eu](https://tuxbot.gnous.eu/) "
                      "| [gnous.eu](https://gnous.eu/) "
                      "| [git](https://git.gnous.eu/gnouseu/tuxbot-bot) "
                      f"| [{Texts('basics', ctx).get('Invite')}](https://discordapp.com/oauth2/authorize?client_id=301062143942590465&scope=bot&permissions=268749888)",
                inline=False
            )

            e.set_footer(text=f'version: {self.bot.version} '
                              f'• prefix: {ctx.prefix}')

        await ctx.send(embed=e)

    ###########################################################################

    @commandExtra(name='credits', aliases=['contributors', 'authors'],
                  category='basics',
                  description=Texts('commands').get('basics._credits'))
    async def _credits(self, ctx: commands.Context):
        e = discord.Embed(
            title=Texts('basics', ctx).get('Contributors'),
            color=0x36393f
        )

        e.add_field(
            name="**Outout#4039** ",
            value="• https://git.gnous.eu/mael        ⠀\n"
                  "• mael@gnous.eu\n"
                  "• [@outoutxyz](https://twitter.com/outouxyz)",
            inline=True
        )
        e.add_field(
            name="**Romain#5117** ",
            value="• https://git.gnous.eu/Romain\n"
                  "• romain@gnous.eu",
            inline=True
        )

        await ctx.send(embed=e)


def setup(bot: TuxBot):
    bot.add_cog(Useful(bot))