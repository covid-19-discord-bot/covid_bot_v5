# coding=utf-8
"""
File designed for you to copy over and over again as a template for new parts of your bot
"""
import discord
from discord.ext import commands

from utils.async_helpers import wrap_in_async
from utils.cog_class import Cog
from utils.ctx_class import MyContext
from utils.maps import map_identifiers


def _(msg, *args, **kwargs):
    return msg.format(*args, **kwargs)


class MapsCommands(Cog):
    @commands.group()
    async def maps(self, ctx: MyContext):
        """
        Fancy, very high quality maps from Our World In Data!
        The maps are 3400 by 2400 pixels.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help("maps")

    @maps.command(aliases=["list", "list_types"])
    async def types(self, ctx: MyContext):
        """
        Shows all maps that can be used in `maps show <map_name>`
        """
        _ = await ctx.get_translate_function()

        map_type_embed = discord.Embed(title=_("Map Types"),
                                       description=_("Use one of these map types when running `{0}maps "
                                                     "show <name>`.", ctx.prefix), color=discord.Color.dark_red())
        for item in map_identifiers:
            map_type_embed.add_field(name=map_identifiers[item][1], value=item)

        await ctx.send(embed=map_type_embed)

    @maps.command()
    async def show(self, ctx: MyContext, map_type: str):
        """
        Show off the maps! See `maps types` to get a list of all maps that can be shown.
        """
        _ = await ctx.get_translate_function()
        map_type = map_type.lower().strip()
        if map_type not in map_identifiers:
            await ctx.send(_("I don't know what map you're looking for! Run `{0}maps types` to see all the "
                             "maps I can show you!", ctx.prefix))
            return
        map_embed = discord.Embed(title=_("Map for {0}", map_identifiers[map_type][1]), color=discord.Color.dark_red())
        try:
            map_buffer = await wrap_in_async(self.bot.maps_api.get_map, map_type, thread_pool=True)
        except KeyError:
            await ctx.reply(_("The bot's still setting up, please wait up to 10 minutes."))
            return
        img_file = discord.File(map_buffer, filename="map.png")
        map_embed.set_image(url="attachment://map.png")
        await ctx.send(embed=map_embed, file=img_file)

    @maps.command(hidden=True)
    @commands.is_owner()
    async def do_update(self, ctx: MyContext):
        msg = await ctx.send(_("Updating maps..."))
        await wrap_in_async(self.bot.maps_api.download_maps, thread_pool=True)
        await msg.edit(content=_("Done!"))


setup = MapsCommands.setup
