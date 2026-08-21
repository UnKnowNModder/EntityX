"""ui components for discord bot."""

from __future__ import annotations

from discord import ButtonStyle, Interaction, User, ui
from discord.utils import get

from tournament import tournament
from tournament.storage import Registration

# registration modal for solo player to input his game account id.


class SoloRegistrationModal(ui.Modal, title="Tournament Solo Registration."):
    """asks for in-game account-id only."""

    account_id = ui.TextInput(
        label="Enter your V2 Account ID",
        required=True,
        placeholder="looks like: a-xxx..",
    )

    def __init__(self, season_id: str):
        super().__init__()
        self.season_id = season_id

    async def on_submit(self, interaction: Interaction):
        registration = Registration(self.season_id)

        # for solo, we use user's display name as team name.
        team_name = interaction.user.display_name
        team_id = registration.register(
            team_name=team_name,
            captain_discord_id=str(interaction.user.id),
            captain_account_id=self.account_id.value,
        )

        if not team_id:
            await interaction.response.send_message(
                "You are already registered in this season.", ephemeral=True
            )
            return

        role = get(interaction.guild.roles, name="Participant")
        await interaction.user.add_roles(role)
        await interaction.response.send_message(
            f"Registered as {team_name}! Join the game server and run `/verify` to verify yourself. ",
            ephemeral=True,
        )


# registration modal for team-captain to input his game account id and team-name


class CaptainRegistrationModal(ui.Modal, title="Tournament Team Registration."):
    """asks for captain's account id and team's name"""

    team_name = ui.TextInput(
        label="Team Name", required=True, placeholder="Enter an unique team name."
    )
    account_id = ui.TextInput(
        label="Enter your V2 Account ID",
        required=True,
        placeholder="looks like: a-xxx..",
    )

    def __init__(self, season_id: str, size: int):
        super().__init__()
        self.season_id = season_id
        self.select = ui.Label(
            text="Select your teammates",
            component= ui.UserSelect(
                placeholder=f"Select {size}",
                min_values=size,
                max_values=size
            )
        )
        self.add_item(self.select)

    async def on_submit(self, interaction: Interaction):
        registration = Registration(self.season_id)

        invited_members = self.select.component.values

        team_id = registration.register(
            team_name=self.team_name.value,
            captain_discord_id=str(interaction.user.id),
            captain_account_id=self.account_id.value,
            invited_members=[str(member.id) for member in invited_members],
        )

        if not team_id:
            await interaction.response.send_message(
                "Failed to register your team! You or one of your teammates might already be registered.",
                ephemeral=True,
            )
            return

        role = get(interaction.guild.roles, name="Participant")
        await interaction.user.add_roles(role)

        view = TeamInvitationView(team_id=team_id)

        await interaction.channel.send(
            f"{' '.join(member.mention for member in invited_members)}, You have been invited to join the team: `{self.team_name.value}` by {interaction.user.mention}",
            view=view,
        )
        await interaction.response.send_message(
            f"Team **{self.team_name.value}** created! Invitation sent to your teammates.! Join the game server and run `/verify` to verify yourself. ",
            ephemeral=True,
        )


# invitation accept modal for team-mates to input their game id.


class InvitationAcceptModal(ui.Modal, title="Accept Team Invitation."):
    """asks for in-game account-id only."""

    account_id = ui.TextInput(
        label="Enter your V2 Account ID",
        required=True,
        placeholder="looks like: a-xxx..",
    )

    def __init__(self, season_id: str):
        super().__init__()
        self.season_id = season_id

    async def on_submit(self, interaction: Interaction):
        registration = Registration(self.season_id)

        success = registration.accept(
            discord_id=str(interaction.user.id), account_id=self.account_id.value
        )

        if not success:
            await interaction.response.send_message(
                "You are not registered in any team.", ephemeral=True
            )
            return

        role = get(interaction.guild.roles, name="Participant")
        await interaction.user.add_roles(role)
        await interaction.response.send_message(
            "You have joined the team! Join the game server and run `/verify` to verify yourself. ",
            ephemeral=True,
        )


# team invitation view for teammates to accept/reject


class TeamInvitationView(ui.View):
    """accept or reject the invitation"""

    def __init__(self, team_id: str):
        super().__init__(timeout=None)
        self.accept_btn.custom_id = f"tiv;accept;{team_id}"
        self.decline_btn.custom_id = f"tiv;decline;{team_id}"

    @ui.button(label="Accept", style=ButtonStyle.success)
    async def accept_btn(self, interaction: Interaction, button: ui.Button):
        season_id = tournament.read().active_season
        db = Registration(season_id=season_id).read()
        user_team_id = db["players"].get(str(interaction.user.id))
        team_id = interaction.data["custom_id"].split(";")[2]
        team = db["teams"].get(team_id)

        if not team:
            await interaction.response.send_message(
                "This team invitation is no longer active.", ephemeral=True
            )
            return

        if user_team_id != team_id:
            await interaction.response.send_message(
                "You are not on the invitation list for this team.", ephemeral=True
            )
            return

        await interaction.response.send_modal(
            InvitationAcceptModal(season_id=season_id)
        )

    @ui.button(label="Decline", style=ButtonStyle.danger)
    async def decline_btn(self, interaction: Interaction, button: ui.Button):
        season_id = tournament.read().active_season
        db = Registration(season_id=season_id).read()
        user_team_id = db["players"].get(str(interaction.user.id))
        team_id = interaction.data["custom_id"].split(";")[2]
        team = db["teams"].get(team_id)

        if not team:
            await interaction.response.send_message(
                "This team invitation is no longer active.", ephemeral=True
            )
            return

        if user_team_id != team_id:
            await interaction.response.send_message(
                "You are not on the invitation list for this team.", ephemeral=True
            )
            return

        role = get(interaction.guild.roles, name="Participant")

        # strip all the members of role.
        for member in team["members"]:
            discord_id = member["discord_id"]
            user = interaction.guild.get_member(discord_id)
            if user and role in user.roles:
                await user.remove_roles(role)

        # delete the team.
        captain, team_name = db.delete(team_id=team_id)

        # disable the btns
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            f"**Invitation Declined**, {interaction.user.mention} declined the invitation for team {team_name}. CAPTAIN: <@{captain}>",
            view=self,
        )
