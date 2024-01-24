from pathlib import Path
from typing import Optional
import os

from xml.etree.ElementTree import Element
import xml.etree.cElementTree as ET

import typer
from typing_extensions import Annotated

app = typer.Typer()


@app.command()
def add_wallpaper(
    path: Annotated[Optional[str], typer.Option()],
    isGlobal: Annotated[Optional[bool], typer.Option()] = False,
):
    # Copy all the files in the path to the wallpapers folder
    global_path = (
        os.path.expanduser("/usr/share")
        if isGlobal
        else os.path.expanduser("~/.local/share")
    )

    if path is None:
        typer.echo("Please specify a path to the wallpaper")
        raise typer.Exit(code=1)

    # Expand the path
    path = os.path.abspath(os.path.expanduser(path)).rstrip("/")

    if not os.path.exists(path):
        typer.echo("The specified path does not exist")
        raise typer.Exit(code=1)

    if not os.path.isdir(path):
        typer.echo("The specified path is not a directory")
        raise typer.Exit(code=1)

    folder_name = os.path.basename(path)

    # get xml_file path
    xml_file = None
    for file in os.listdir(path):
        if file.endswith(".xml"):
            xml_file = os.path.join(path, file)
            print(path, file, xml_file)
            break

    if xml_file is None:
        typer.echo("No xml file found in the specified path")
        raise typer.Exit(code=1)

    # wallpaper path
    wallpaper_path = os.path.join(global_path, "backgrounds/gnome")

    # Put all the jpg files in a new folder inside the wallpaper path
    new_folder = os.path.join(wallpaper_path, folder_name)
    os.mkdir(new_folder)

    # Copy all the jpg files in the path to the new folder
    path_files = os.listdir(path)
    for file in path_files:
        if file.endswith(".jpg") or file.endswith(".png"):
            os.system(
                "cp "
                + os.path.join(path, file).replace(" ", "\\ ")
                + " "
                + new_folder.replace(" ", "\\ ")
            )

    # Copy the xml file in the path to the wallpaper path
    os.system(
        "cp "
        + xml_file.replace(" ", "\\ ")
        + " "
        + os.path.join(wallpaper_path, f"{folder_name}.xml").replace(" ", "\\ ")
    )

    # Update the xml file with the new file paths
    update_xml_file(
        os.path.join(wallpaper_path, f"{folder_name}.xml"),
        wallpaper_path,
    )

    # Create an xml file for gnome-backgrounds
    background_properties_path = os.path.join(
        global_path, "gnome-background-properties"
    )
    new_xml_file = os.path.join(background_properties_path, f"{folder_name}.xml")
    generate_xml(new_xml_file, folder_name)


def generate_xml(filePath: str, wallpaper_name: str):
    # Create the root element
    root = ET.Element("wallpapers")

    # Create the wallpaper element
    wallpaper = ET.SubElement(root, "wallpaper", deleted="false")

    # Create child elements for the wallpaper
    name = ET.SubElement(wallpaper, "name")
    name.text = wallpaper_name

    filename = ET.SubElement(wallpaper, "filename")
    filename.text = (
        f"/home/flyingdelta/.local/share/backgrounds/gnome/{wallpaper_name}.xml"
    )

    options = ET.SubElement(wallpaper, "options")
    options.text = "zoom"

    # Create an ElementTree object
    tree = ET.ElementTree(root)

    # Create the doctype element
    doctype = '<!DOCTYPE wallpapers SYSTEM "gnome-wp-list.dtd">'
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'

    # Write the XML to a file
    with open(filePath, "wb") as file:
        file.write(xml_declaration.encode("utf-8"))
        file.write(doctype.encode("utf-8"))
        tree.write(file, encoding="utf-8")

    print("XML generated successfully!")


def update_file_paths(element: Element, custom_string: str):
    if element.tag == "file" or element.tag == "from" or element.tag == "to":
        # Update the file path by replacing the old prefix with the custom string
        if element.text is not None:
            element.text = "/".join(element.text.strip("/").split("/")[-2:])
            element.text = os.path.join(custom_string, element.text)

    for child in element:
        update_file_paths(child, custom_string)


def update_xml_file(file_path: str, custom_string: str):
    custom_string = custom_string
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Traverse the XML tree and update file paths
    update_file_paths(root, custom_string)

    # Save the modified XML back to the file
    tree.write(file_path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    app()
