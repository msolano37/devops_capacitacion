package com.paymentchain.billing;

import javax.annotation.PostConstruct;
import net.dv8tion.jda.api.JDABuilder;
import net.dv8tion.jda.api.entities.Activity;
import net.dv8tion.jda.api.requests.GatewayIntent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class DiscordBotRunner {
    private static final Logger LOGGER = LoggerFactory.getLogger(DiscordBotRunner.class);

    private final UfcSchedulePoster schedulePoster;
    private final String botToken;

    public DiscordBotRunner(UfcSchedulePoster schedulePoster,
                            @Value("${discord.bot-token:}") String botToken) {
        this.schedulePoster = schedulePoster;
        this.botToken = botToken;
    }

    @PostConstruct
    public void startBot() {
        if (botToken == null || botToken.isBlank()) {
            LOGGER.warn("Discord bot token not configured. Bot commands are disabled.");
            return;
        }
        JDABuilder.createDefault(botToken, GatewayIntent.GUILD_MESSAGES, GatewayIntent.MESSAGE_CONTENT)
            .setActivity(Activity.watching("carteleras UFC"))
            .addEventListeners(new DiscordCommandListener(schedulePoster))
            .build();
    }
}
