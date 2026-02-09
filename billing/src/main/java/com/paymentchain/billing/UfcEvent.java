package com.paymentchain.billing;

import java.time.ZonedDateTime;

public class UfcEvent {
    private final String name;
    private final ZonedDateTime date;
    private final String venue;

    public UfcEvent(String name, ZonedDateTime date, String venue) {
        this.name = name;
        this.date = date;
        this.venue = venue;
    }

    public String getName() {
        return name;
    }

    public ZonedDateTime getDate() {
        return date;
    }

    public String getVenue() {
        return venue;
    }
}
