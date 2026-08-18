# Flutter client

Android and Windows client for the School Inventory API.

Generate standard platform runner files once after cloning:

```bash
python ../scripts/bootstrap_flutter.py
flutter pub get
flutter run -d windows
```

The backend URL is configured at build time:

```bash
flutter run -d android --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```
