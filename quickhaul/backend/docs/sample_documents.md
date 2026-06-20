# MongoDB Collections and Sample Documents

## users
```json
{
  "_id": "ObjectId('...')",
  "name": "Asha Verma",
  "email": "asha@example.com",
  "password_hash": "$2b$12$....",
  "created_at": "2026-04-22T16:00:00Z"
}
```

## drivers
```json
{
  "_id": "ObjectId('...')",
  "name": "Ravi Kumar",
  "phone": "9999988888",
  "vehicle_type": "van",
  "is_available": true,
  "created_at": "2026-04-22T16:00:00Z"
}
```

## pricing_rules
```json
{
  "_id": "ObjectId('...')",
  "transport_type": "truck",
  "base_rate_per_km": 4.0,
  "weight_rate_per_kg": 0.4,
  "active": true
}
```

## bookings
```json
{
  "_id": "ObjectId('...')",
  "user_id": "6807ca....",
  "from_location": "Delhi",
  "to_location": "Noida",
  "transport_type": "van",
  "goods_type": "furniture",
  "distance_km": 28.0,
  "weight_kg": 120.0,
  "price": 118.0,
  "status": "ASSIGNED",
  "driver_id": "6807d0....",
  "created_at": "2026-04-22T16:00:00Z"
}
```
