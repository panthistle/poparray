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


from random import random, seed, shuffle
from mathutils import Quaternion, Vector

from . import mpath as ModPATH


# ------------------------------------------------------------------------------
#
# ----------------------------- POPEX HELPERS ----------------------------------


def falloff_lists(npts, dct):
    itm = dct["itm"]
    reps = dct["reps"]
    k = dct["idx"]
    repfoff = dct["repfoff"]
    foffstp = dct["repfstp"]
    mir = dct["mir"]
    iinc = dct["gap"] + 1
    ditm = itm
    dstp = 1
    if dct["rev"]:
        iinc = -iinc
        ditm = -itm
        dstp = -1
    i_lst = [i % npts for i in range(k, k + ditm, dstp)]
    if (itm == 1) or (dct["ease"] == "OFF"):
        v_lst = [1] * itm
    else:
        div = itm if dct["cyc"] else itm - 1
        v_lst = ModPATH.it_list(dct["ease"], 1 / div, dct["exp"], mir, itm)
        sref = dct["reflect"]
        if sref == "3":
            v_lst = [i if i >= 0.5 else 1 - i for i in v_lst]
        elif sref == "2":
            v_lst = [i if i <= 0.5 else 1 - i for i in v_lst]
        elif sref == "1":
            v_lst = [1 - i for i in v_lst]
    if (npts == itm) or (reps == 1):
        return i_lst, v_lst
    tlst = v_lst.copy()
    if foffstp > 1:
        fct = 1
        for i in range(reps - 1):
            foff = 1
            fct += 1
            if fct > foffstp:
                fct = 1
                foff = repfoff
            k = i_lst[-1] + iinc
            i_lst += [j % npts for j in range(k, k + ditm, dstp)]
            tlst = [foff * j for j in tlst]
            v_lst += tlst
        return i_lst[:npts], v_lst[:npts]
    for i in range(reps - 1):
        k = i_lst[-1] + iinc
        i_lst += [j % npts for j in range(k, k + ditm, dstp)]
        tlst = [repfoff * j for j in tlst]
        v_lst += tlst
    return i_lst[:npts], v_lst[:npts]


def shuffparams_get(npts, params):
    ids, fvs = falloff_lists(npts, params)
    rndval = params["rndval"]
    shuff = False
    if params["rnduse"]:
        seed(params["rndseed"])
        if rndval:
            fvs = [(1 - random() * rndval) * v for v in fvs]
        shuff = params["rndshuff"]
    return ids, fvs, shuff


def params_get(npts, params):
    ids, fvs = falloff_lists(npts, params)
    rndval = params["rndval"]
    if params["rnduse"] and rndval:
        seed(params["rndseed"])
        fvs = [(1 - random() * rndval) * v for v in fvs]
    return ids, fvs


def attitude_rots(locs, cyclic, dv, up="X"):
    if cyclic:
        l2 = locs[-1]
        locs.append(locs[0])
    else:
        l2 = locs[0] + (locs[0] - locs[1])
        locs.append(locs[-1] + (locs[-1] - locs[-2]))
    a = locs[1] - l2
    if isinstance(dv, str):
        rots = [a.to_track_quat(dv, up)]
        for i in range(1, len(locs) - 1):
            rots.append((locs[i + 1] - locs[i - 1]).to_track_quat(dv, up))
    else:
        rots = [dv.rotation_difference(a)]
        for i in range(1, len(locs) - 1):
            b = locs[i + 1] - locs[i - 1]
            rots.append(a.rotation_difference(b) @ rots[-1])
            a = b
    locs.pop()
    return rots


def dv_from_axis(axis):
    if axis in ("X", "-X"):
        return Vector((1, 0, 0)) if axis == "X" else Vector((-1, 0, 0))
    if axis in ("Y", "-Y"):
        return Vector((0, 1, 0)) if axis == "Y" else Vector((0, -1, 0))
    return Vector((0, 0, 1)) if axis == "Z" else Vector((0, 0, -1))


# ------------------------------------------------------------------------------
#
# ---------------------------- POPEX CLASS -------------------------------------


class PopEx:
    """path-on-path class"""

    # INITIALIZE

    def __init__(self, pool_dct, path_dct, prof_dct):
        self._set_path(path_dct)
        self._set_profile(prof_dct)
        self._set_associations(pool_dct)

    def _set_path(self, dct):
        self._path = getattr(ModPATH, dct["provider"].capitalize())(dct)
        self._pathlocs = self._path.get_locs()
        self._rings = self._path.npts
        self._pathrots = [Quaternion()] * self._rings
        self._pathedlocs = []
        self._pathed_lopts = []
        self._pathedrots = []
        self._pathed_rpivs = []
        self._pathed_raxes = []
        self._pathed_ropts = []
        self._pathed_rfacs = []

    def _set_profile(self, dct):
        if dct:
            #  [2d array]
            self._profile = getattr(ModPATH, dct["provider"].capitalize())(dct)
            self._rpts = self._profile.npts
            self._proflocs = self._profile.get_locs()
            self._profrots = [[Quaternion()] * self._rpts for _ in range(self._rings)]
            self._fullrots = [[Quaternion()] * self._rings for _ in range(self._rpts)]
            self._profedlocs = []
            self._profed_lopts = []
            self._profedrots = []
            self._profed_rpivs = []
            self._profed_raxes = []
            self._profed_ropts = []
            self._profed_rfacs = []
        else:
            #  [1d array]
            self._profile = None
            self._rpts = 1

    def _set_associations(self, dct):
        self._items = self._rings * self._rpts
        self._pathori = dct["pathori"]
        self._path_track = dct["pathori_track"]
        self._path_trackvec = dv_from_axis(dct["pathori_track"])
        self._path_up = dct["pathori_up"]
        self._path_upfixed = dct["pathori_upfixed"]
        self._defsca = dct["defsca"]
        self._objedscas = []
        self._objedlocs = []
        self._objed_lopts = []
        self._objedrots = []
        self._objed_raxes = []
        self._objed_rfacs = []
        if self._profile:
            self._profori = dct["profori"]
            self._prof_track = dct["profori_track"]
            self._prof_trackvec = dv_from_axis(dct["profori_track"])
            self._prof_up = dct["profori_up"]
            self._prof_upfixed = dct["profori_upfixed"]
            self._fullori = dct["fullori"]

    # MODIFY

    def path_edrotations(self, dct):
        axis = dct["axis"]
        self._pathed_raxes.append(axis)
        self._pathed_rpivs.append(Vector(dct["pivot"]))
        self._pathed_ropts.append([dct["bbatt"], dct["brots"]])
        nids, nfvs = params_get(self._rings, dct["nprams"])
        lst = [0] * self._rings
        for i, f in zip(nids, nfvs):
            lst[i] = f
        self._pathed_rfacs.append(lst)
        angle = dct["angle"]
        self._pathedrots.append([Quaternion(axis, angle * f) for f in lst])

    def _pathedloc_get(self, locs, dct):
        nids, nfvs = params_get(self._rings, dct["nprams"])
        axis = Vector(dct["axis"]) * dct["fac"]
        if dct["abs_move"]:
            for i, f in zip(nids, nfvs):
                if f:
                    locs[i] = axis * f
        else:
            for i, f in zip(nids, nfvs):
                if f:
                    dv = self._pathlocs[i].normalized()
                    for j in range(3):
                        locs[i][j] = dv[j] * axis[j] * f
        return locs

    def path_edlocations(self, dct):
        self._pathed_lopts.append(dct["bbatt"])
        locs = [Vector() for _ in range(self._rings)]
        if not dct["fac"]:
            self._pathedlocs.append(locs)
            return
        self._pathedlocs.append(self._pathedloc_get(locs, dct))

    def prof_edrotations(self, dct):
        axis = dct["axis"]
        self._profed_raxes.append(axis)
        self._profed_rpivs.append(Vector(dct["pivot"]))
        self._profed_ropts.append([dct["bbatt"], dct["brots"]])
        nids, nfvs, shuff = shuffparams_get(self._rings, dct["nprams"])
        ids, fvs = params_get(self._rpts, dct["iprams"])
        lst = [[0] * self._rpts for _ in range(self._rings)]
        for i, f in zip(nids, nfvs):
            if f:
                if shuff:
                    shuffle(fvs)
                for j, p in zip(ids, fvs):
                    if p:
                        lst[i][j] = f * p
        self._profed_rfacs.append(lst)
        ang = dct["angle"]
        self._profedrots.append([[Quaternion(axis, ang * i) for i in fl] for fl in lst])

    def _profedloc_get(self, locs, dct):
        ids, fvs = params_get(self._rpts, dct["iprams"])
        nids, nfvs, shuff = shuffparams_get(self._rings, dct["nprams"])
        axis = Vector(dct["axis"]) * dct["fac"]
        if dct["abs_move"]:
            for i, f in zip(nids, nfvs):
                if f:
                    if shuff:
                        shuffle(fvs)
                    for j, p in zip(ids, fvs):
                        if p:
                            locs[i][j] = axis * (f * p)
        else:
            for i, f in zip(nids, nfvs):
                if f:
                    if shuff:
                        shuffle(fvs)
                    for j, p in zip(ids, fvs):
                        if p:
                            dv = self._proflocs[j].normalized()
                            df = f * p
                            for k in range(2):
                                locs[i][j][k] = dv[k] * axis[k] * df
        return locs

    def prof_edlocations(self, dct):
        self._profed_lopts.append(dct["bbatt"])
        locs = [[Vector() for _ in range(self._rpts)] for _ in range(self._rings)]
        if not dct["fac"]:
            self._profedlocs.append(locs)
            return
        self._profedlocs.append(self._profedloc_get(locs, dct))

    def obj_edrotations(self, dct):
        axis = dct["axis"]
        self._objed_raxes.append(axis)
        lst = [0] * self._items
        if self._rpts == 1:
            nids, nfvs = params_get(self._rings, dct["nprams"])
            for i, f in zip(nids, nfvs):
                if f:
                    lst[i] = f
        else:
            nids, nfvs, shuff = shuffparams_get(self._rings, dct["nprams"])
            ids, fvs = params_get(self._rpts, dct["iprams"])
            for i, f in zip(nids, nfvs):
                if f:
                    loop = i * self._rpts
                    if shuff:
                        shuffle(fvs)
                    for j, p in zip(ids, fvs):
                        if p:
                            lst[loop + j] = f * p
        self._objed_rfacs.append(lst)
        ang = dct["angle"]
        self._objedrots.append([Quaternion(axis, ang * i) for i in lst])

    def _objedloc_get(self, locs, dct):
        axis = Vector(dct["axis"]) * dct["fac"]
        if self._rpts == 1:
            nids, nfvs = params_get(self._rings, dct["nprams"])
            for i, f in zip(nids, nfvs):
                if f:
                    locs[i] = axis * f
            return locs
        nids, nfvs, shuff = shuffparams_get(self._rings, dct["nprams"])
        ids, fvs = params_get(self._rpts, dct["iprams"])
        for i, f in zip(nids, nfvs):
            if f:
                loop = i * self._rpts
                if shuff:
                    shuffle(fvs)
                for j, p in zip(ids, fvs):
                    if p:
                        locs[loop + j] = axis * (f * p)
        return locs

    def obj_edlocations(self, dct):
        self._objed_lopts.append(dct["abs_move"])
        locs = [Vector()] * self._items
        val = sum(1 if i else 0 for i in dct["axis"]) * dct["fac"]
        if not val:
            self._objedlocs.append(locs)
            return
        self._objedlocs.append(self._objedloc_get(locs, dct))

    def _objedsca_get(self, scas, dct):
        axis = [dct["fac"] * i for i in dct["axis"]]
        if self._rpts == 1:
            nids, nfvs = params_get(self._rings, dct["nprams"])
            for i, f in zip(nids, nfvs):
                if f:
                    scas[i] = [f * j for j in axis]
            return scas
        nids, nfvs, shuff = shuffparams_get(self._rings, dct["nprams"])
        ids, fvs = params_get(self._rpts, dct["iprams"])
        for i, f in zip(nids, nfvs):
            if f:
                loop = i * self._rpts
                if shuff:
                    shuffle(fvs)
                for j, p in zip(ids, fvs):
                    if p:
                        scas[loop + j] = [f * p * j for j in axis]
        return scas

    def obj_edscales(self, dct):
        scas = [[0, 0, 0]] * self._items
        val = sum(1 if i else 0 for i in dct["axis"]) * dct["fac"]
        if not val:
            self._objedscas.append(scas)
            return
        self._objedscas.append(self._objedsca_get(scas, dct))

    # RETURN

    @property
    def rings(self):
        return self._rings

    @property
    def rpts(self):
        return self._rpts

    def _rots_update(self, orilocs, provider, dv, track, up, fixup, rots_0, shqu):
        offset = provider.ioff
        sid = provider.npts - offset
        locs = orilocs[sid:] + orilocs[:sid]
        if fixup:
            rots = attitude_rots(locs, provider.closed, track, up)
        else:
            rots = attitude_rots(locs, provider.closed, dv)
        rots = rots[offset:] + rots[:offset]
        if shqu:
            for q0, q in zip(rots_0, rots):
                if q0.dot(q) < 0:
                    q.negate()
        return rots

    def _prof_loc_lists(self):
        locs = [self._proflocs] * self._rings
        noatt = []
        for boo, vls in zip(self._profed_lopts, self._profedlocs):
            if boo:
                locs = [[a + b for a, b in zip(la, lb)] for la, lb in zip(locs, vls)]
            elif noatt:
                noatt = [[a + b for a, b in zip(la, lb)] for la, lb in zip(noatt, vls)]
            else:
                noatt = vls
        return locs, noatt

    def _prof_edrots_locs(self, shqu):
        locs, edlocs = self._prof_loc_lists()
        befo_r, rots, afte_p = [], [], []
        for ols, qls, p in zip(
            self._profed_ropts, self._profedrots, self._profed_rpivs
        ):
            if ols[0] == "before":
                if ols[1] in {"locs", "both"}:
                    locs = [
                        [q @ (v - p) + p for q, v in zip(rl, vl)]
                        for rl, vl in zip(qls, locs)
                    ]
                    if edlocs:
                        edlocs = [
                            [q @ (v - p) + p for q, v in zip(rl, vl)]
                            for rl, vl in zip(qls, edlocs)
                        ]
                if ols[1] in {"rots", "both"}:
                    if befo_r:
                        befo_r = [
                            [q @ b for q, b in zip(ql, bl)]
                            for ql, bl in zip(qls, befo_r)
                        ]
                    else:
                        befo_r = qls
            else:
                if ols[1] in {"locs", "both"}:
                    afte_p.append([qls, p])
                if ols[1] in {"rots", "both"}:
                    if rots:
                        rots = [
                            [q @ a for q, a in zip(ql, al)] for ql, al in zip(qls, rots)
                        ]
                    else:
                        rots = qls
        if self._profori:
            dv = self._prof_trackvec
            track = self._prof_track
            up = self._prof_up
            upfix = self._prof_upfixed
            for i, (vls, qls) in enumerate(zip(locs, self._profrots)):
                self._profrots[i] = self._rots_update(
                    vls, self._profile, dv, track, up, upfix, qls, shqu
                )
            if rots:
                rots = [
                    [q @ a for q, a in zip(ql, al)]
                    for ql, al in zip(rots, self._profrots)
                ]
            else:
                rots = self._profrots
            if befo_r:
                rots = [[q @ b for q, b in zip(ql, bl)] for ql, bl in zip(rots, befo_r)]
        elif befo_r:
            if rots:
                rots = [[q @ b for q, b in zip(ql, bl)] for ql, bl in zip(rots, befo_r)]
            else:
                rots = befo_r
        if edlocs:
            locs = [[a + b for a, b in zip(la, lb)] for la, lb in zip(locs, edlocs)]
        for qls, p in afte_p:
            locs = [
                [q @ (v - p) + p for q, v in zip(ql, vl)] for ql, vl in zip(qls, locs)
            ]
        return locs, rots

    def _array2d_data(self, pa_l, pa_r, shqu):
        locs, rots = self._prof_edrots_locs(shqu)
        if pa_r:
            locs = [q @ loc + v for q, v, vls in zip(pa_r, pa_l, locs) for loc in vls]
        else:
            locs = [loc + v for v, vls in zip(pa_l, locs) for loc in vls]
        if self._fullori:
            frts = []
            dv = self._path_trackvec
            track = self._path_track
            up = self._path_up
            upfix = self._path_upfixed
            if rots:
                for i, qls in enumerate(self._fullrots):
                    vls = locs[i : self._items : self._rpts]
                    self._fullrots[i] = self._rots_update(
                        vls, self._path, dv, track, up, upfix, qls, shqu
                    )
                    rbp = [rots[j][i] for j in range(self._rings)]
                    frts += [a @ b for a, b in zip(self._fullrots[i], rbp)]
            else:
                for i, qls in enumerate(self._fullrots):
                    vls = locs[i : self._items : self._rpts]
                    self._fullrots[i] = self._rots_update(
                        vls, self._path, dv, track, up, upfix, qls, shqu
                    )
                    frts += self._fullrots[i]
            frts = [
                q
                for i in range(self._rings)
                for q in frts[i : self._items : self._rings]
            ]
            return locs, frts
        if pa_r:
            if rots:
                return locs, [q @ rot for q, qls in zip(pa_r, rots) for rot in qls]
            return locs, [q for q in pa_r for _ in range(self._rpts)]
        return locs, [q for qls in rots for q in qls]

    def _path_loc_lists(self):
        locs = self._pathlocs
        noatt = []
        for boo, vls in zip(self._pathed_lopts, self._pathedlocs):
            if boo:
                locs = [loc + v for loc, v in zip(locs, vls)]
            elif noatt:
                noatt = [loc + v for loc, v in zip(noatt, vls)]
            else:
                noatt = vls
        return locs, noatt

    def _path_edrots_locs(self, shqu):
        locs, edlocs = self._path_loc_lists()
        befo_r, rots, afte_p = [], [], []
        for ols, qls, p in zip(
            self._pathed_ropts, self._pathedrots, self._pathed_rpivs
        ):
            if ols[0] == "before":
                if ols[1] in {"locs", "both"}:
                    locs = [q @ (v - p) + p for q, v in zip(qls, locs)]
                    if edlocs:
                        edlocs = [q @ (v - p) + p for q, v in zip(qls, edlocs)]
                if ols[1] in {"rots", "both"}:
                    if befo_r:
                        befo_r = [q @ b for q, b in zip(qls, befo_r)]
                    else:
                        befo_r = qls
            else:
                if ols[1] in {"locs", "both"}:
                    afte_p.append([qls, p])
                if ols[1] in {"rots", "both"}:
                    if rots:
                        rots = [q @ a for q, a in zip(qls, rots)]
                    else:
                        rots = qls
        if self._pathori:
            dv = self._path_trackvec
            track = self._path_track
            up = self._path_up
            upfix = self._path_upfixed
            self._pathrots = self._rots_update(
                locs, self._path, dv, track, up, upfix, self._pathrots, shqu
            )
            if rots:
                rots = [q @ a for q, a in zip(rots, self._pathrots)]
            else:
                rots = self._pathrots
            if befo_r:
                rots = [q @ b for q, b in zip(rots, befo_r)]
        elif befo_r:
            if rots:
                rots = [q @ b for q, b in zip(rots, befo_r)]
            else:
                rots = befo_r
        if edlocs:
            locs = [loc + v for loc, v in zip(locs, edlocs)]
        for qls, p in afte_p:
            locs = [q @ (v - p) + p for q, v in zip(qls, locs)]
        return locs, rots

    def _obj_loc_lists(self):
        wlocs = []
        olocs = []
        for boo, vls in zip(self._objed_lopts, self._objedlocs):
            if boo:
                if wlocs:
                    wlocs = [a + b for a, b in zip(wlocs, vls)]
                else:
                    wlocs = vls
            elif olocs:
                olocs = [a + b for a, b in zip(olocs, vls)]
            else:
                olocs = vls
        return wlocs, olocs

    def get_data(self, shqu=False):
        locs, rots = self._path_edrots_locs(shqu)
        if self._profile:
            locs, rots = self._array2d_data(locs, rots, shqu)
        if self._objedrots:
            obrs = self._objedrots[0]
            for qls in self._objedrots[1:]:
                obrs = [a @ b for a, b in zip(qls, obrs)]
            if rots:
                rots = [a @ b for a, b in zip(rots, obrs)]
            else:
                rots = obrs
        wcs, ocs = self._obj_loc_lists()
        if ocs:
            if rots:
                locs = [a + q @ b for a, q, b in zip(locs, rots, ocs)]
            else:
                locs = [a + b for a, b in zip(locs, ocs)]
        if wcs:
            locs = [a + b for a, b in zip(locs, wcs)]
        if not rots:
            rots = [Quaternion()] * self._items
        return locs, rots

    def get_objscas(self):
        scas = [self._defsca] * self._items
        for lst in self._objedscas:
            scas = [[a + b for a, b in zip(la, lb)] for la, lb in zip(scas, lst)]
        return scas

    def get_path_locations(self, use_edits):
        locs = self._pathlocs
        if not use_edits:
            return locs
        for lst in self._pathedlocs:
            locs = [v + l for v, l in zip(locs, lst)]
        for opt, qls, piv in zip(
            self._pathed_ropts, self._pathedrots, self._pathed_rpivs
        ):
            if opt[1] in {"locs", "both"}:
                locs = [q @ (v - piv) + piv for q, v in zip(qls, locs)]
        return locs

    # ANIMATION

    def path_anim_update(self, *args):
        self._path.anim_update(*args)
        self._pathlocs = self._path.get_locs()

    def prof_anim_update(self, *args):
        self._profile.anim_update(*args)
        self._proflocs = self._profile.get_locs()

    def pathedrot_anim_angle(self, angle, ufac, idx):
        rots = self._pathedrots[idx]
        axis = self._pathed_raxes[idx]
        if ufac:
            fls = self._pathed_rfacs[idx]
            self._pathedrots[idx] = [
                rot @ Quaternion(axis, f * angle) for rot, f in zip(rots, fls)
            ]
        else:
            q = Quaternion(axis, angle)
            self._pathedrots[idx] = [rot @ q for rot in rots]

    def pathedloc_anim_data(self, dct, idx):
        locs = [Vector() for _ in range(self._rings)]
        if not dct["fac"]:
            self._pathedlocs[idx] = locs
            return
        self._pathedlocs[idx] = self._pathedloc_get(locs, dct)

    def profedrot_anim_angle(self, angle, ufac, idx):
        rots = self._profedrots[idx]
        axis = self._profed_raxes[idx]
        if ufac:
            fls = self._profed_rfacs[idx]
            self._profedrots[idx] = [
                [rot @ Quaternion(axis, f * angle) for rot, f in zip(rl, fl)]
                for rl, fl in zip(rots, fls)
            ]
        else:
            q = Quaternion(axis, angle)
            self._profedrots[idx] = [[rot @ q for rot in rl] for rl in rots]

    def profedloc_anim_data(self, dct, idx):
        locs = [[Vector() for _ in range(self._rpts)] for _ in range(self._rings)]
        if not dct["fac"]:
            self._profedlocs[idx] = locs
            return
        self._profedlocs[idx] = self._profedloc_get(locs, dct)

    def objedrot_anim_angle(self, angle, ufac, idx):
        rots = self._objedrots[idx]
        axis = self._objed_raxes[idx]
        if ufac:
            fls = self._objed_rfacs[idx]
            self._objedrots[idx] = [
                rot @ Quaternion(axis, f * angle) for rot, f in zip(rots, fls)
            ]
        else:
            q = Quaternion(axis, angle)
            self._objedrots[idx] = [rot @ q for rot in rots]

    def objedloc_anim_data(self, dct, idx):
        locs = [Vector()] * self._items
        val = sum(1 if i else 0 for i in dct["axis"]) * dct["fac"]
        if not val:
            self._objedlocs[idx] = locs
            return
        self._objedlocs[idx] = self._objedloc_get(locs, dct)

    def objedsca_anim_data(self, dct, idx):
        scas = [[0, 0, 0]] * self._items
        val = sum(1 if i else 0 for i in dct["axis"]) * dct["fac"]
        if not val:
            self._objedscas[idx] = scas
            return
        self._objedscas[idx] = self._objedsca_get(scas, dct)
