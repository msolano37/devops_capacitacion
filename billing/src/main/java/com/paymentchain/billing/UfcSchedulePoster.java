package com.paymentchain.billing;

import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class UfcSchedulePoster {
    private static final Logger LOGGER = LoggerFactory.getLogger(UfcSchedulePoster.class);

    private final UfcEventsService eventsService;
    private final DiscordWebhookClient webhookClient;
    private final DateTimeFormatter formatter;

    public UfcSchedulePoster(UfcEventsService eventsService,
                             DiscordWebhookClient webhookClient,
                             @Value("${ufc.date-format:dd MMM yyyy HH:mm z}") String dateFormat) {
        this.eventsService = eventsService;
        this.webhookClient = webhookClient;
        this.formatter = DateTimeFormatter.ofPattern(dateFormat, new Locale("es", "ES"));
    }

    @Scheduled(cron = "${ufc.cron:0 0 9 * * *}")
    public void postUpcomingEvents() {
        String message = buildUpcomingEventsMessage();
        if (message == null) {
            LOGGER.info("No upcoming UFC events found.");
            return;
        }
        webhookClient.sendMessage(message);
    }

    public String buildUpcomingEventsMessage() {
        List<UfcEvent> events = eventsService.fetchUpcomingEvents();
        if (events.isEmpty()) {
            return null;
        }
        return buildMessage(events);
    }

    public String buildMessage(List<UfcEvent> events) {
        StringBuilder message = new StringBuilder("**Próximas carteleras de UFC**\n");
        for (UfcEvent event : events) {
            message.append("• ")
                .append(event.getName())
                .append(" — ")
                .append(event.getDate().format(formatter))
                .append(" — ")
                .append(event.getVenue())
                .append("\n");
        }
        return message.toString();
    }
}
