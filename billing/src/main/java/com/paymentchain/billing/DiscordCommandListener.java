package com.paymentchain.billing;

import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
import org.springframework.lang.NonNull;

public class DiscordCommandListener extends ListenerAdapter {
    private final UfcSchedulePoster schedulePoster;

    public DiscordCommandListener(UfcSchedulePoster schedulePoster) {
        this.schedulePoster = schedulePoster;
    }

    @Override
    public void onMessageReceived(@NonNull MessageReceivedEvent event) {
        if (event.getAuthor().isBot()) {
            return;
        }
        String content = event.getMessage().getContentRaw().trim();
        if (!content.equalsIgnoreCase("!ufc")
            && !content.equalsIgnoreCase("!ufc cartelera")
            && !content.equalsIgnoreCase("!ufc carteleras")) {
            return;
        }
        String message = schedulePoster.buildUpcomingEventsMessage();
        if (message == null) {
            event.getChannel().sendMessage("No hay carteleras futuras disponibles.").queue();
            return;
        }
        event.getChannel().sendMessage(message).queue();
    }
}
