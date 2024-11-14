##############################################################################
#                                                                            #
#   PopArray for Blender  --  Copyright (C) 2024  Pan Thistle                #
#                                                                            #
#   This program is free software: you can redistribute it and/or modify     #
#   it under the terms of the GNU General Public License as published by     #
#   the Free Software Foundation, either version 3 of the License, or        #
#   (at your option) any later version.                                      #
#                                                                            #
#   This program is distributed in the hope that it will be useful,          #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#   GNU General Public License for more details.                             #
#                                                                            #
#   You should have received a copy of the GNU General Public License        #
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.   #
#                                                                            #
##############################################################################


# ------------------------------------------------------------------------------
#
# ----------------------------- IMPORTS ----------------------------------------


import bpy

from random import seed, randint, uniform
from mathutils import Vector

from . import mdata as ModDATA


# ------------------------------------------------------------------------------
#
# --------------------------------- ARRAY --------------------------------------


def create_oblist(src, items, coll):
    name = f"{src.name}_copy"
    for i in range(items):
        ob = src.copy()
        ob.name = name
        ob.rotation_mode = "QUATERNION"
        ob.hide_viewport = False
        ob.hide_render = False
        ob.hide_select = False
        ob.hide_set(False)
        coll.objects.link(ob)
        ob.select_set(False)
    return coll.objects[:]


# ------------------------------------------------------------------------------
#
# ------------------------- SCENE UPDATES --------------------------------------


def noiz_locs(locs, axis, amp, ns):
    val = sum(1 if i else 0 for i in axis) * amp
    if not val:
        return locs
    seed(ns)
    return [
        loc + Vector((i * uniform(-amp, amp) if i else 0 for i in axis)) for loc in locs
    ]


def new_pop_instance(pool):
    path = pool.path
    path.clean = (path.provider != "custom") or (len(path.pathed.upv) > 2)
    if not path.clean:
        raise Exception("user path, not enough verts")
    if pool.use_profile:
        prof = pool.prof
        prof.clean = (prof.provider != "custom") or (len(prof.profed.upv) > 2)
        if not prof.clean:
            raise Exception("user profile, not enough verts")
        prof_dct = prof.to_dct()
    else:
        prof_dct = None
    pop = ModDATA.PopEx(pool.to_dct(), path.to_dct(), prof_dct)
    return pop


def update_deps_onedim(pg, rings):
    for item in pg:
        item.nprams.npts = rings


def update_deps_twodim(pg, rings, rpts):
    for item in pg:
        item.nprams.npts = rings
        item.iprams.npts = rpts


def update_associations(pool, rings, rpts):
    pool.path.pathed.npts = rings
    update_deps_onedim(pool.pathloc, rings)
    update_deps_onedim(pool.pathrot, rings)
    if pool.use_profile:
        pool.prof.profed.npts = rpts
        update_deps_twodim(pool.profloc, rings, rpts)
        update_deps_twodim(pool.profrot, rings, rpts)
        update_deps_twodim(pool.obloc, rings, rpts)
        update_deps_twodim(pool.obrot, rings, rpts)
        update_deps_twodim(pool.obsca, rings, rpts)
    else:
        update_deps_onedim(pool.obloc, rings)
        update_deps_onedim(pool.obrot, rings)
        update_deps_onedim(pool.obsca, rings)


def pop_update(pop, pool):
    for item in pool.pathrot:
        if item.active:
            pop.path_edrotations(item.to_dct())
    for item in pool.pathloc:
        if item.active:
            pop.path_edlocations(item.to_dct())
    for item in pool.obrot:
        if item.active:
            pop.obj_edrotations(item.to_dct())
    for item in pool.obloc:
        if item.active:
            pop.obj_edlocations(item.to_dct())
    for item in pool.obsca:
        if item.active:
            pop.obj_edscales(item.to_dct())
    if pool.use_profile:
        for item in pool.profrot:
            if item.active:
                pop.prof_edrotations(item.to_dct())
        for item in pool.profloc:
            if item.active:
                pop.prof_edlocations(item.to_dct())


def rngids_calc(npts, k, itm, gap, reps):
    ids = [i % npts for i in range(k, k + itm)]
    if (npts == itm) or (reps < 2):
        return ids
    iinc = gap + 1
    for i in range(reps - 1):
        k = ids[-1] + iinc
        ids += [j % npts for j in range(k, k + itm)]
    return ids[:npts]


def range_indices_update(rngs, rings, rpts, items):
    rngs.rbeg = rngs.rbeg % rings
    rngs.ritm = min(rngs.ritm, rings)
    rngs.rgap = min(rngs.rgap, rings - rngs.ritm)
    grp = rngs.ritm + rngs.rgap
    hi = rings // grp
    hi += 0 if rings % grp < rngs.ritm else 1
    rngs.rstp = min(rngs.rstp, hi)
    inds = rngids_calc(rings, rngs.rbeg, rngs.ritm, rngs.rgap, rngs.rstp)
    if rpts > 1:
        rngs.pbeg = rngs.pbeg % rpts
        rngs.pitm = min(rngs.pitm, rpts)
        rngs.pgap = min(rngs.pgap, rpts - rngs.pitm)
        grp = rngs.pitm + rngs.pgap
        hi = rpts // grp
        hi += 0 if rpts % grp < rngs.pitm else 1
        rngs.pstp = min(rngs.pstp, hi)
        pids = rngids_calc(rpts, rngs.pbeg, rngs.pitm, rngs.pgap, rngs.pstp)
        inds = [r * rpts + p for r in inds for p in pids]
    if rngs.invert:
        inds_set = set(inds)
        inds = [i for i in range(items) if i not in inds_set]
    if rngs.rndsel:
        seed(rngs.nseed)
        inds_len = len(inds)
        inds = [inds[randint(0, inds_len - 1)] for _ in range(inds_len)]
    inds_set = set(i for i in inds if i < items)
    rngs.sindz_set(inds_set)
    return len(inds_set)


def array_update(pool, pop, oblst, items, sindz_on):
    pop_update(pop, pool)
    locs, rots = pop.get_data()
    noiz = pool.noiz
    if noiz.active:
        locs = noiz_locs(locs, noiz.vfac, noiz.ampli, noiz.nseed)
    scas = pop.get_objscas()
    if sindz_on:
        sindz = pool.rngs.sindz_get()
        locs = [locs[i] for i in range(items) if i in sindz]
        rots = [rots[i] for i in range(items) if i in sindz]
        scas = [scas[i] for i in range(items) if i in sindz]
    for ob, loc, rot, sca in zip(oblst, locs, rots, scas):
        ob.location = loc
        ob.rotation_quaternion = rot
        ob.scale = sca


def scene_update(scene):
    pool = scene.ptdblnpopa_pool
    pop = new_pop_instance(pool)
    rings = pop.rings
    rpts = pop.rpts
    popitems = rings * rpts
    sindz_on = pool.rngs.active
    if sindz_on:
        dummy = range_indices_update(pool.rngs, rings, rpts, popitems)
    oblst = pool.setcoll.objects[:]
    array_update(pool, pop, oblst, popitems, sindz_on)


def scene_update_newset(scene, replace=False, rename_coll=False):
    pool = scene.ptdblnpopa_pool
    pop = new_pop_instance(pool)
    rings = pop.rings
    rpts = pop.rpts
    update_associations(pool, rings, rpts)
    popitems = rings * rpts
    nobs = popitems
    sindz_on = pool.rngs.active
    if sindz_on:
        nobs = range_indices_update(pool.rngs, rings, rpts, popitems)
    if pool.setcoll and replace:
        name = pool.setcoll_name if rename_coll else pool.setcoll.name
        bpy.data.collections.remove(pool.setcoll)
        print("---- poparray replace: delete trash")
        bpy.ops.outliner.orphans_purge(do_recursive=True)
    else:
        name = pool.setcoll_name
    pool.setcoll = bpy.data.collections.new(name)
    scene.collection.children.link(pool.setcoll)
    oblst = create_oblist(pool.sample_ob, nobs, pool.setcoll)
    array_update(pool, pop, oblst, popitems, sindz_on)


def create_path_object(scene):
    pool = scene.ptdblnpopa_pool
    use_edits = pool.custom_path_use_edits
    pop = new_pop_instance(pool)
    if use_edits:
        for item in pool.pathrot:
            if item.active:
                pop.path_edrotations(item.to_dct())
        for item in pool.pathloc:
            if item.active:
                pop.path_edlocations(item.to_dct())
    verts = pop.get_path_locations(use_edits)
    lid = pop.rings - 1
    edges = [(i, i + 1) for i in range(lid)]
    name = "cpath_mesh"
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, edges, [])
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
