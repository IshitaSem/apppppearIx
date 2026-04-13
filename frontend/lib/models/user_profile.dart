class UserProfile {
  String name;
  String email;
  String? phone;
  String gender;
  String size;
  String aesthetic;
  List<String>? favoriteColors;

  UserProfile({
    required this.name,
    required this.email,
    this.phone,
    required this.gender,
    required this.size,
    required this.aesthetic,
    this.favoriteColors,
  });

  // Optional: convert to Map (useful later for saving data)
  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'email': email,
      'phone': phone,
      'gender': gender,
      'size': size,
      'aesthetic': aesthetic,
      'favoriteColors': favoriteColors,
    };
  }

  // Optional: create object from Map
  factory UserProfile.fromMap(Map<String, dynamic> map) {
    return UserProfile(
      name: map['name'] ?? '',
      email: map['email'] ?? '',
      phone: map['phone'],
      gender: map['gender'] ?? '',
      size: map['size'] ?? '',
      aesthetic: map['aesthetic'] ?? '',
      favoriteColors: map['favoriteColors'] != null
          ? List<String>.from(map['favoriteColors'])
          : null,
    );
  }
}
