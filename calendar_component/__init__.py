import os
import streamlit.components.v1 as components

# Skapa en _RELEASE variabel för att avgöra om vi kör i dev eller prod mode
_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "calendar_component",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend")
    _component_func = components.declare_component("calendar_component", path=build_dir)


def clickable_calendar(week_data, key=None):
    """
    Skapar en klickbar kalendervy där användaren kan klicka på en specifik tid.

    Parameters:
    -----------
    week_data : dict
        Dictionary med kalenderdatan för veckan
    key : str
        Unik nyckel för komponenten

    Returns:
    --------
    dict or None
        Dict med 'date' och 'time' om användaren klickat, annars None
    """
    component_value = _component_func(week_data=week_data, key=key, default=None)
    return component_value
