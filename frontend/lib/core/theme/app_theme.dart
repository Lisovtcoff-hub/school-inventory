import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData light() {
    const bg = Color(0xFFF5F5F5);
    const text = Color(0xFF2E2E2E);
    const graphite = Color(0xFF3A3A3A);
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: bg,
      colorScheme: ColorScheme.fromSeed(seedColor: graphite, brightness: Brightness.light),
      appBarTheme: const AppBarTheme(backgroundColor: Colors.white, foregroundColor: text, elevation: 0),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFFDADADA))),
        filled: true,
        fillColor: Colors.white,
      ),
      cardTheme: CardThemeData(color: Colors.white, elevation: 0, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16), side: const BorderSide(color: Color(0xFFE1E1E1)))),
      filledButtonTheme: FilledButtonThemeData(style: FilledButton.styleFrom(backgroundColor: graphite, foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)))),
      outlinedButtonTheme: OutlinedButtonThemeData(style: OutlinedButton.styleFrom(foregroundColor: text, side: const BorderSide(color: Color(0xFFDADADA)), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)))),
    );
  }
}
