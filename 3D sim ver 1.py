# -*- coding: utf-8 -*-
"""
Created on Tue May 12 18:55:57 2026

@author: Eric
"""

from vpython import *
import random
import math

# ---------------- CONFIG ----------------

INITIAL_ISOTOPES = 80
INITIAL_NEUTRONS = 10
SIMULATION_STEPS = 600

REACTOR_RADIUS = 6
FISSION_PROBABILITY = 0.12
NEUTRONS_PER_FISSION = 2
NEUTRON_SPEED = 0.08

ATOM_RADIUS = 0.13
NEUTRON_RADIUS = 0.06

# ---------------- SCENE ----------------

scene.title = "Toy 3D Chain Reaction Visualiser"
scene.width = 1000
scene.height = 700
scene.background = color.black
scene.camera.pos = vector(0, -14, 7)
scene.camera.axis = vector(0, 14, -7)

# transparent chamber
sphere(
    pos=vector(0, 0, 0),
    radius=REACTOR_RADIUS,
    color=color.white,
    opacity=0.08
)


# ---------------- HELPERS ----------------

def random_point_in_sphere(radius):
    while True:
        p = vector(
            random.uniform(-radius, radius),
            random.uniform(-radius, radius),
            random.uniform(-radius, radius)
        )
        if mag(p) <= radius:
            return p

def random_direction():
    theta = random.uniform(0, 2 * math.pi)
    z = random.uniform(-1, 1)
    r = math.sqrt(1 - z * z)
    return vector(
        r * math.cos(theta),
        r * math.sin(theta),
        z
    )

# ---------------- OBJECTS ----------------

isotopes = []
neutrons = []

for i in range(INITIAL_ISOTOPES):
    obj = sphere(
        pos=random_point_in_sphere(REACTOR_RADIUS * 0.85),
        radius=ATOM_RADIUS,
        color=color.green
    )
    isotopes.append({
        "object": obj,
        "active": True
    })

for i in range(INITIAL_NEUTRONS):
    obj = sphere(
        pos=random_point_in_sphere(REACTOR_RADIUS * 0.5),
        radius=NEUTRON_RADIUS,
        color=color.cyan,
        make_trail=True,
        retain=25
    )
    neutrons.append({
        "object": obj,
        "velocity": random_direction() * NEUTRON_SPEED,
        "active": True
    })

stats = label(
    pos=vector(-6.5, 6.5, 0),
    text="",
    height=12,
    box=False,
    color=color.white
)

# ---------------- SIMULATION LOOP ----------------

spent_count = 0
total_created_neutrons = INITIAL_NEUTRONS

for step in range(SIMULATION_STEPS):
    rate(60)

    new_neutrons = []

    for neutron in neutrons:
        if not neutron["active"]:
            continue

        n_obj = neutron["object"]
        n_obj.pos += neutron["velocity"]

        # bounce off boundary
        if mag(n_obj.pos) > REACTOR_RADIUS:
            normal = norm(n_obj.pos)
            neutron["velocity"] = neutron["velocity"] - 2 * dot(neutron["velocity"], normal) * normal
            n_obj.pos = normal * REACTOR_RADIUS

        # collision with isotope
        for isotope in isotopes:
            if not isotope["active"]:
                continue

            atom_obj = isotope["object"]
            if mag(n_obj.pos - atom_obj.pos) < 0.35:
                if random.random() < FISSION_PROBABILITY:
                    isotope["active"] = False
                    atom_obj.color = color.gray(0.35)
                    atom_obj.radius = ATOM_RADIUS * 0.8
                    spent_count += 1

                    # flash
                    flash = sphere(
                        pos=atom_obj.pos,
                        radius=0.35,
                        color=color.orange,
                        opacity=0.45
                    )

                    # consume incoming neutron
                    neutron["active"] = False
                    n_obj.visible = False

                    # release new neutrons
                    for _ in range(NEUTRONS_PER_FISSION):
                        new_obj = sphere(
                            pos=atom_obj.pos,
                            radius=NEUTRON_RADIUS,
                            color=color.cyan,
                            make_trail=True,
                            retain=25
                        )
                        new_neutrons.append({
                            "object": new_obj,
                            "velocity": random_direction() * NEUTRON_SPEED,
                            "active": True
                        })
                        total_created_neutrons += 1

                    break

        # fade flash objects roughly by deleting old orange flashes
        for obj in scene.objects:
            if hasattr(obj, "color") and obj.color == color.orange:
                obj.opacity -= 0.02
                if obj.opacity <= 0:
                    obj.visible = False

    neutrons.extend(new_neutrons)

    active_atoms = sum(1 for atom in isotopes if atom["active"])
    active_neutrons = sum(1 for neutron in neutrons if neutron["active"])

    stats.text = (
        f"Step: {step}\n"
        f"Initial isotopes: {INITIAL_ISOTOPES}\n"
        f"Spent isotopes: {spent_count}\n"
        f"Remaining isotopes: {active_atoms}\n"
        f"Total neutrons created: {total_created_neutrons}\n"
        f"Active neutrons: {active_neutrons}"
    )

print("Simulation complete.")