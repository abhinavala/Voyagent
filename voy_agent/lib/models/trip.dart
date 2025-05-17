import 'flight.dart';
import 'hotel.dart';
import 'car.dart';

class Trip {
  final String title;
  final String subtitle;
  final Flight flight;
  final Hotel hotel;
  final Car car;

  Trip({
    required this.title,
    required this.subtitle,
    required this.flight,
    required this.hotel,
    required this.car,
  });

  double get totalCost =>
      flight.price + hotel.pricePerNight * hotel.nights + car.pricePerDay * car.days;
}