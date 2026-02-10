#!/usr/bin/env python3
"""
streamlit run character_database_streamlit.py
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path


class Character:

    def __init__(self, name="", char_class="", level=1, strength=10,
                 dexterity=10, constitution=10, intelligence=10,
                 wisdom=10, charisma=10):
        self.name = name
        self.char_class = char_class
        self.level = level
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma
        self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()

    def to_dict(self):
        return {
            'name': self.name, 'class': self.char_class, 'level': self.level,
            'strength': self.strength, 'dexterity': self.dexterity,
            'constitution': self.constitution, 'intelligence': self.intelligence,
            'wisdom': self.wisdom, 'charisma': self.charisma,
            'created_date': self.created_date, 'modified_date': self.modified_date
        }

    @classmethod
    def from_dict(cls, data):
        char = cls(
            name=data.get('name', ''), char_class=data.get('class', ''),
            level=data.get('level', 1), strength=data.get('strength', 10),
            dexterity=data.get('dexterity', 10), constitution=data.get('constitution', 10),
            intelligence=data.get('intelligence', 10), wisdom=data.get('wisdom', 10),
            charisma=data.get('charisma', 10)
        )
        char.created_date = data.get('created_date', datetime.now().isoformat())
        char.modified_date = data.get('modified_date', datetime.now().isoformat())
        return char


class CharacterDatabase:

    def __init__(self, data_dir="character_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.characters = {}
        self.load_all_characters()

    def load_all_characters(self):
        self.characters = {}
        for file_path in self.data_dir.glob("*.json"):
            with open(file_path, 'r') as f:
                data = json.load(f)
                char = Character.from_dict(data)
                self.characters[char.name] = char

    def save_character(self, character):
        character.modified_date = datetime.now().isoformat()
        filename = f"{character.name.replace(' ', '_')}.json"
        with open(self.data_dir / filename, 'w') as f:
            json.dump(character.to_dict(), f, indent=2)
        self.characters[character.name] = character

    def delete_character(self, name):
        filename = f"{name.replace(' ', '_')}.json"
        file_path = self.data_dir / filename
        if file_path.exists():
            file_path.unlink()
        del self.characters[name]

    def get_character(self, name):
        return self.characters.get(name)

    def list_characters(self):
        return sorted(self.characters.values(), key=lambda c: c.name.lower())

CLASSES = ['Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk',
           'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard']

st.set_page_config(page_title="Character Database", layout="wide")
st.title("Character Database Manager")

with st.expander("How to use this app"):
    step = st.radio("", [
        "Welcome",
        "Step 1: Creating a Character",
        "Step 2: Saving Characters",
        "Step 3: Loading and Managing",
        "Additional Features"
    ], horizontal=True, label_visibility="collapsed")

    steps = {
        "Welcome": """
**Welcome to Character Database Manager!**

This tutorial will guide you through the basic workflow:
1. Create a new character
2. Save the character to disk
3. Load and edit existing characters

This process allows you to manage your game characters efficiently,
reducing administrative burden and letting you focus on the game.
        """,
        "Step 1: Creating a Character": """
**Creating a Character**

1. Click **+ New Character** at the top of the character list
2. Fill in all required fields (Name, Class, Level, and Stats)
3. Click **Save** when ready

> TIP: You can edit an existing character by clicking **Edit** next to it in the list
        """,
        "Step 2: Saving Characters": """
**Saving Characters**

When you click Save:
1. Your character is saved to a JSON file
2. The file is stored in the `character_data` folder
3. You'll see a confirmation message

> NOTE: Unsaved changes are lost if you navigate away before saving
        """,
        "Step 3: Loading and Managing": """
**Loading and Managing**

To work with existing characters:
1. Characters are listed on the main screen
2. Click a character's name to expand their stats
3. Click **Edit** to load them into the form
4. Click **Delete** to remove them

> TIP: The list shows essential info; expand a character for full stat details
        """,
        "Additional Features": """
**Additional Features**

- Characters are sorted alphabetically in the list
- Ability scores are displayed as a stat block when expanded
- The edit form pre-fills with the character's current values

You're ready to start!
        """
    }
    st.markdown(steps[step])

db = CharacterDatabase()

if "view" not in st.session_state:
    st.session_state.view = "list"
if "editing" not in st.session_state:
    st.session_state.editing = None

# Character list
if st.session_state.view == "list":
    col_title, col_btn = st.columns([5, 1])
    col_title.subheader("Characters")
    if col_btn.button("+ New Character", use_container_width=True):
        st.session_state.editing = None
        st.session_state.view = "form"
        st.rerun()

    characters = db.list_characters()
    if not characters:
        st.info("No characters yet. Click '+ New Character' to create one.")
    else:
        for char in characters:
            with st.expander(f"{char.name} -- {char.char_class} (Level {char.level})"):
                cols = st.columns(6)
                for col, (stat, val) in zip(cols, [
                    ("STR", char.strength), ("DEX", char.dexterity),
                    ("CON", char.constitution), ("INT", char.intelligence),
                    ("WIS", char.wisdom), ("CHA", char.charisma)
                ]):
                    col.metric(stat, val)

                col_edit, col_del, _ = st.columns([1, 1, 6])
                if col_edit.button("Edit", key=f"edit_{char.name}"):
                    st.session_state.editing = char.name
                    st.session_state.view = "form"
                    st.rerun()
                if col_del.button("Delete", key=f"del_{char.name}"):
                    db.delete_character(char.name)
                    st.rerun()

# Create / Edit form
elif st.session_state.view == "form":
    editing_name = st.session_state.editing
    existing = db.get_character(editing_name) if editing_name else None

    st.subheader(f"Editing: {existing.name}" if existing else "New Character")

    name = st.text_input("Name", value=existing.name if existing else "")
    char_class = st.selectbox("Class", CLASSES, index=CLASSES.index(existing.char_class) if existing and existing.char_class in CLASSES else 0)
    level = st.slider("Level", 1, 20, existing.level if existing else 1)

    st.markdown("**Ability Scores**")
    col1, col2, col3 = st.columns(3)
    strength     = col1.number_input("Strength",     3, 18, existing.strength     if existing else 10)
    dexterity    = col2.number_input("Dexterity",    3, 18, existing.dexterity    if existing else 10)
    constitution = col3.number_input("Constitution", 3, 18, existing.constitution if existing else 10)
    intelligence = col1.number_input("Intelligence", 3, 18, existing.intelligence if existing else 10)
    wisdom       = col2.number_input("Wisdom",       3, 18, existing.wisdom       if existing else 10)
    charisma     = col3.number_input("Charisma",     3, 18, existing.charisma     if existing else 10)

    col_save, col_back = st.columns([1, 5])
    if col_save.button("Save", type="primary"):
        if not name.strip():
            st.error("Name is required.")
        else:
            char = Character(name, char_class, level, strength, dexterity,
                             constitution, intelligence, wisdom, charisma)
            if existing:
                char.created_date = existing.created_date
            db.save_character(char)
            st.session_state.editing = None
            st.session_state.view = "list"
            st.rerun()

    if col_back.button("Back to list"):
        st.session_state.editing = None
        st.session_state.view = "list"
        st.rerun()
