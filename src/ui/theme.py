from nicegui import ui


def apply_theme():
    """
    Applies global styles and Tailwind configuration to the application head.
    Should be called once at application startup or layout initialization.
    """
    ui.add_head_html("""
        <script>
            // Configure Tailwind to use class-based dark mode
            tailwind.config = { darkMode: "class" }
            
            // Force applies dark mode classes immediately to avoid flash of light mode
            // We assume default is Dark, as set in layout.py
            document.body.classList.add("dark");
            document.body.classList.add("body--dark");
        </script>
        <style>
            body { margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
            .nicegui-content { padding: 0 !important; }
            
            /* Alignment fix for Quasar buttons with icons */
            .nav-btn .q-btn__content { justify-content: flex-start; }
            
            /* Custom Scrollbar */
            ::-webkit-scrollbar { width: 8px; height: 8px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
            ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
            
            /* Dark Mode Scrollbar Overrides */
            .dark ::-webkit-scrollbar-thumb { background: #475569; }
            .dark ::-webkit-scrollbar-thumb:hover { background: #64748b; }
        </style>
    """)


async def toggle_dark_mode(dark_mode_element):
    """
    Toggles dark mode for the entire application.
    Syncs both NiceGUI's (Quasar) dark mode and Tailwind's class-based dark mode.

    Args:
        dark_mode_element: The persistent ui.dark_mode() instance created in the layout.
    """
    # Simply toggle the Value. NiceGUI handles the rest for Quasar.
    # treating None as False implies we default to Light if unknown
    # But usually we initialize it as True.
    if dark_mode_element.value is None:
        dark_mode_element.value = True  # Default pivot

    dark_mode_element.value = not dark_mode_element.value
    new_value = dark_mode_element.value

    # Sync Tailwind's 'dark' class based on the NEW value
    is_dark = str(new_value).lower()

    await ui.run_javascript(f"""
        const isDark = {is_dark};
        if (isDark) {{
            // Add Dark Mode classes
            document.body.classList.add("dark");
            document.body.classList.add("body--dark");
            
            // Remove Light Mode classes
            document.body.classList.remove("body--light");
        }} else {{
            // Remove Dark Mode classes
            document.body.classList.remove("dark");
            document.body.classList.remove("body--dark");
            
            // Add Light Mode classes
            document.body.classList.add("body--light");
        }}
    """)
