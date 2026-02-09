package com.paymentchain.billing;

import com.fasterxml.jackson.databind.JsonNode;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class UfcEventsService {
    private static final Logger LOGGER = LoggerFactory.getLogger(UfcEventsService.class);

    private final RestTemplate restTemplate;
    private final String eventsUrl;
    private final ZoneId zoneId;

    public UfcEventsService(RestTemplate restTemplate,
                            @Value("${ufc.events-url}") String eventsUrl,
                            @Value("${ufc.timezone:UTC}") String timezone) {
        this.restTemplate = restTemplate;
        this.eventsUrl = eventsUrl;
        this.zoneId = ZoneId.of(timezone);
    }

    public List<UfcEvent> fetchUpcomingEvents() {
        JsonNode payload = restTemplate.getForObject(eventsUrl, JsonNode.class);
        List<UfcEvent> events = new ArrayList<>();
        if (payload == null) {
            LOGGER.warn("UFC events payload is empty from {}", eventsUrl);
            return events;
        }
        JsonNode eventsNode = payload.path("events");
        if (!eventsNode.isArray()) {
            LOGGER.warn("UFC events payload does not contain an events array.");
            return events;
        }
        ZonedDateTime now = ZonedDateTime.now(zoneId);
        for (JsonNode eventNode : eventsNode) {
            String name = eventNode.path("name").asText("Evento UFC");
            String dateText = eventNode.path("date").asText(null);
            ZonedDateTime eventDate = parseDate(dateText);
            if (eventDate == null || eventDate.isBefore(now)) {
                continue;
            }
            String state = eventNode.path("status").path("type").path("state").asText("");
            boolean isUpcoming = state.isEmpty() || "pre".equalsIgnoreCase(state);
            if (!isUpcoming) {
                continue;
            }
            String venue = eventNode.path("competitions").path(0).path("venue").path("fullName")
                .asText("Por confirmar");
            events.add(new UfcEvent(name, eventDate, venue));
        }
        events.sort(Comparator.comparing(UfcEvent::getDate));
        return events;
    }

    private ZonedDateTime parseDate(String dateText) {
        if (dateText == null || dateText.isBlank()) {
            return null;
        }
        try {
            return OffsetDateTime.parse(dateText).atZoneSameInstant(zoneId);
        } catch (Exception ex) {
            LOGGER.warn("Unable to parse UFC event date: {}", dateText, ex);
            return null;
        }
    }
}
