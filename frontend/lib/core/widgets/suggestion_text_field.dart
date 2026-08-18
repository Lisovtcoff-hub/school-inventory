import 'package:flutter/material.dart';

/// TextField с подсказками из уже заведённой техники.
/// Это удобно для школ, где много одинаковых ноутбуков, принтеров или кабинетов.
class SuggestionTextField extends StatefulWidget {
  final TextEditingController controller;
  final String label;
  final List<String> suggestions;
  final bool required;
  final int maxLines;

  const SuggestionTextField({
    super.key,
    required this.controller,
    required this.label,
    required this.suggestions,
    this.required = false,
    this.maxLines = 1,
  });

  @override
  State<SuggestionTextField> createState() => _SuggestionTextFieldState();
}

class _SuggestionTextFieldState extends State<SuggestionTextField> {
  final focusNode = FocusNode();

  @override
  void dispose() {
    focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.suggestions.isEmpty || widget.maxLines > 1) {
      return TextField(
        controller: widget.controller,
        maxLines: widget.maxLines,
        decoration: InputDecoration(labelText: widget.required ? '${widget.label} *' : widget.label),
      );
    }

    return RawAutocomplete<String>(
      textEditingController: widget.controller,
      focusNode: focusNode,
      optionsBuilder: (value) {
        final q = value.text.trim().toLowerCase();
        final base = widget.suggestions.where((s) => s.trim().isNotEmpty).toSet().toList()..sort();
        if (q.isEmpty) return base.take(8);
        return base.where((s) => s.toLowerCase().contains(q)).take(8);
      },
      onSelected: (value) => widget.controller.text = value,
      fieldViewBuilder: (context, controller, focus, onSubmitted) => TextField(
        controller: controller,
        focusNode: focus,
        decoration: InputDecoration(
          labelText: widget.required ? '${widget.label} *' : widget.label,
          suffixIcon: const Icon(Icons.manage_search, size: 18),
        ),
      ),
      optionsViewBuilder: (context, onSelected, options) => Align(
        alignment: Alignment.topLeft,
        child: Material(
          elevation: 4,
          borderRadius: BorderRadius.circular(12),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 280, maxHeight: 240),
            child: ListView.builder(
              padding: EdgeInsets.zero,
              shrinkWrap: true,
              itemCount: options.length,
              itemBuilder: (context, index) {
                final option = options.elementAt(index);
                return ListTile(
                  dense: true,
                  title: Text(option),
                  onTap: () => onSelected(option),
                );
              },
            ),
          ),
        ),
      ),
    );
  }
}
