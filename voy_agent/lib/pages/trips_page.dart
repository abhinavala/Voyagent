import 'package:flutter/material.dart';
import 'package:voy_agent/models/trip.dart';
import 'package:voy_agent/models/flight.dart';
import 'package:voy_agent/models/hotel.dart';
import 'package:voy_agent/models/car.dart';
import 'package:voy_agent/pages/chat_page.dart';
import 'package:voy_agent/pages/trip_details_page.dart';

// Model for user profile
class Profile {
  final String firstName;
  final String lastName;
  final String cardNumber;
  final String cardExpiry;   // MM/YY
  final String cardCvv;
  final String street;
  final String city;
  final String state;
  final String zip;
  final String driverLicense;

  Profile({
    required this.firstName,
    required this.lastName,
    required this.cardNumber,
    required this.cardExpiry,
    required this.cardCvv,
    required this.street,
    required this.city,
    required this.state,
    required this.zip,
    required this.driverLicense,
  });
}

class TripsPage extends StatefulWidget {
  const TripsPage({Key? key}) : super(key: key);
  @override
  _TripsPageState createState() => _TripsPageState();
}

class _TripsPageState extends State<TripsPage> {
  final List<Trip> trips = [
    Trip(
      title: 'Paris Getaway',
      subtitle: 'May 5 - May 8',
      flight: Flight(
        airline: 'Air Paris', from: 'NYC', to: 'Paris',
        departureDate: '2025-05-05', returnDate: '2025-05-08', price: 850.00,
      ),
      hotel: Hotel(
        name: 'Hotel Louvre', location: 'Paris Center',
        pricePerNight: 200.00, nights: 3,
      ),
      car: Car(
        model: 'Peugeot 308', company: 'Rent-a-Car',
        pricePerDay: 50.00, days: 3,
      ),
    ),
    Trip(
      title: 'Tokyo Adventure',
      subtitle: 'June 10 - June 15',
      flight: Flight(
        airline: 'Japan Air', from: 'NYC', to: 'Tokyo',
        departureDate: '2025-06-10', returnDate: '2025-06-15', price: 1200.00,
      ),
      hotel: Hotel(
        name: 'Shinjuku Hotel', location: 'Shinjuku',
        pricePerNight: 180.00, nights: 5,
      ),
      car: Car(
        model: 'Toyota Prius', company: 'Nippon Rent-a-Car',
        pricePerDay: 45.00, days: 5,
      ),
    ),
  ];

  List<Profile> profiles = [];
  Profile? selectedProfile;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Trips')),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            const DrawerHeader(
              decoration: BoxDecoration(color: Colors.blue),
              child: Text('Profiles', style: TextStyle(color: Colors.white, fontSize: 24)),
            ),
            ListTile(
              leading: const Icon(Icons.person_add),
              title: const Text('Create New Profile'),
              onTap: () async {
                Navigator.of(context).pop();
                final newProfile = await Navigator.of(context).push<Profile>(
                  MaterialPageRoute(builder: (_) => const CreateProfilePage()),
                );
                if (newProfile != null) {
                  setState(() {
                    profiles.add(newProfile);
                    selectedProfile = newProfile;
                  });
                }
              },
            ),
            ExpansionTile(
              leading: const Icon(Icons.account_circle),
              title: const Text('Choose Profile'),
              children: profiles.map((p) {
                final isSelected = p == selectedProfile;
                return ListTile(
                  leading: const Icon(Icons.person),
                  title: Text('${p.firstName} ${p.lastName}'),
                  trailing: isSelected ? const Icon(Icons.check, color: Colors.green) : null,
                  onTap: () {
                    setState(() {
                      selectedProfile = p;
                    });
                    Navigator.of(context).pop();
                  },
                );
              }).toList(),
            ),
          ],
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ListView.builder(
          itemCount: trips.length + 1,
          itemBuilder: (context, index) {
            if (index == 0) {
              return Card(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                color: Colors.white,
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  leading: const Icon(Icons.add, color: Colors.blue),
                  title: const Text('Create New Trip'),
                  onTap: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const ChatPage()),
                    );
                  },
                ),
              );
            }
            final trip = trips[index - 1];
            return Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              color: Colors.white,
              margin: const EdgeInsets.only(bottom: 12),
              child: ListTile(
                title: Text(trip.title),
                subtitle: Text(trip.subtitle),
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => TripDetailsPage(trip: trip)),
                  );
                },
              ),
            );
          },
        ),
      ),
    );
  }
}

// Form page for creating a new profile
class CreateProfilePage extends StatefulWidget {
  const CreateProfilePage({Key? key}) : super(key: key);

  @override
  _CreateProfilePageState createState() => _CreateProfilePageState();
}

class _CreateProfilePageState extends State<CreateProfilePage> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameCtl = TextEditingController();
  final _lastNameCtl = TextEditingController();
  final _cardCtl = TextEditingController();
  final _expiryCtl = TextEditingController();
  final _cvvCtl = TextEditingController();
  final _streetCtl = TextEditingController();
  final _cityCtl = TextEditingController();
  final _stateCtl = TextEditingController();
  final _zipCtl = TextEditingController();
  final _licenseCtl = TextEditingController();

  @override
  void dispose() {
    _firstNameCtl.dispose();
    _lastNameCtl.dispose();
    _cardCtl.dispose();
    _expiryCtl.dispose();
    _cvvCtl.dispose();
    _streetCtl.dispose();
    _cityCtl.dispose();
    _stateCtl.dispose();
    _zipCtl.dispose();
    _licenseCtl.dispose();
    super.dispose();
  }

  void _save() {
    if (!_formKey.currentState!.validate()) return;
    final profile = Profile(
      firstName: _firstNameCtl.text.trim(),
      lastName: _lastNameCtl.text.trim(),
      cardNumber: _cardCtl.text.trim(),
      cardExpiry: _expiryCtl.text.trim(),
      cardCvv: _cvvCtl.text.trim(),
      street: _streetCtl.text.trim(),
      city: _cityCtl.text.trim(),
      state: _stateCtl.text.trim(),
      zip: _zipCtl.text.trim(),
      driverLicense: _licenseCtl.text.trim(),
    );
    Navigator.of(context).pop(profile);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('New Profile')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _firstNameCtl,
                      decoration: const InputDecoration(labelText: 'First Name'),
                      validator: (v) => v!.isEmpty ? 'Enter first name' : null,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _lastNameCtl,
                      decoration: const InputDecoration(labelText: 'Last Name'),
                      validator: (v) => v!.isEmpty ? 'Enter last name' : null,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _cardCtl,
                decoration: const InputDecoration(labelText: 'Credit Card Number'),
                keyboardType: TextInputType.number,
                validator: (v) => v!.isEmpty ? 'Enter card number' : null,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _expiryCtl,
                      decoration: const InputDecoration(labelText: 'Expiry (MM/YY)'),
                      keyboardType: TextInputType.datetime,
                      validator: (v) => v!.isEmpty ? 'Enter expiry date' : null,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _cvvCtl,
                      decoration: const InputDecoration(labelText: 'CVV'),
                      keyboardType: TextInputType.number,
                      obscureText: true,
                      validator: (v) => v!.isEmpty ? 'Enter CVV' : null,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _streetCtl,
                decoration: const InputDecoration(labelText: 'Street Address'),
                validator: (v) => v!.isEmpty ? 'Enter street address' : null,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _cityCtl,
                      decoration: const InputDecoration(labelText: 'City'),
                      validator: (v) => v!.isEmpty ? 'Enter city' : null,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _stateCtl,
                      decoration: const InputDecoration(labelText: 'State'),
                      validator: (v) => v!.isEmpty ? 'Enter state' : null,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _zipCtl,
                      decoration: const InputDecoration(labelText: 'ZIP Code'),
                      keyboardType: TextInputType.number,
                      validator: (v) => v!.isEmpty ? 'Enter ZIP code' : null,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _licenseCtl,
                decoration: const InputDecoration(labelText: 'Driver License #'),
                validator: (v) => v!.isEmpty ? 'Enter license #' : null,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _save,
                child: const Text('Save Profile'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
