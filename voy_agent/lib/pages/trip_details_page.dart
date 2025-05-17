import 'package:flutter/material.dart';
import 'package:voy_agent/models/trip.dart';

class TripDetailsPage extends StatelessWidget {
  final Trip trip;
  const TripDetailsPage({Key? key, required this.trip}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(trip.title)),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Flight Details
          Card(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Flight', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text('${trip.flight.from} → ${trip.flight.to}'),
                  Text('Departure: ${trip.flight.departureDate}'),
                  Text('Return: ${trip.flight.returnDate}'),
                  Text('Airline: ${trip.flight.airline}'),
                  Text('Price: \$${trip.flight.price.toStringAsFixed(2)}'),
                ],
              ),
            ),
          ),

          // Hotel Details
          Card(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Hotel', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text(trip.hotel.name),
                  Text('Location: ${trip.hotel.location}'),
                  Text('Nights: ${trip.hotel.nights}'),
                  Text('Price/night: \$${trip.hotel.pricePerNight.toStringAsFixed(2)}'),
                  Text('Total: \$${(trip.hotel.pricePerNight * trip.hotel.nights).toStringAsFixed(2)}'),
                ],
              ),
            ),
          ),

          // Car Rental Details
          Card(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Car Rental', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text(trip.car.model),
                  Text('Company: ${trip.car.company}'),
                  Text('Days: ${trip.car.days}'),
                  Text('Price/day: \$${trip.car.pricePerDay.toStringAsFixed(2)}'),
                  Text('Total: \$${(trip.car.pricePerDay * trip.car.days).toStringAsFixed(2)}'),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),
          // Checkout Button
          ElevatedButton(
            onPressed: () {
              // TODO: trigger booking flow
            },
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: Text(
              'Checkout (\$${trip.totalCost.toStringAsFixed(2)})',
              style: const TextStyle(fontSize: 16),
            ),
          ),
        ],
      ),
    );
  }
}
