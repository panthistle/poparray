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


# ------------------------------------------------------------------------------
#
# -------------------------------- BMUIL ---------------------------------------


# ---- USER LISTS


class PTDBLNPOPA_UL_pathloc(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPA_UL_pathrot(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPA_UL_profloc(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPA_UL_profrot(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPA_UL_obloc(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPA_UL_obrot(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPA_UL_obsca(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPA_UL_trax(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "RADIOBUT_ON" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


# ---- PANELS


def basels_ok(scene, pool):
    if not pool.sample_ob or (pool.sample_ob.name not in scene.objects):
        return False
    if not pool.setcoll:
        return False
    return True


def arrayset_ok(scene):
    pool = scene.ptdblnpopa_pool
    if not basels_ok(scene, pool):
        return False
    coll = pool.setcoll
    nobs = sum(1 for ob in coll.objects if ob.type in pool.OBJ_SUPPORT)
    if pool.rngs.active:
        items = len(pool.rngs.sindz_get())
    else:
        rpts = pool.prof.profed.npts if pool.use_profile else 1
        items = pool.path.pathed.npts * rpts
    return nobs == items


def ed_panels_ok(pool):
    prof_eval = pool.prof.clean if pool.use_profile else True
    return pool.path.clean and prof_eval


def coll_ops_tmpl(bcol, pool, cname, iname, coll_ob, coll_idx, ops_on):
    col = bcol.column(align=True)
    row = col.row(align=True)
    rc = row.column(align=True)
    c_op = rc.operator("ptdblnpopa.citem_add")
    c_op.cname = cname
    c_op.iname = iname
    boo = coll_ob[coll_idx].active if ops_on else False
    rc = row.column(align=True)
    rc.enabled = boo
    c_op = rc.operator("ptdblnpopa.citem_copy")
    c_op.cname = cname
    c_op.iname = iname
    c = col.column(align=True)
    c.enabled = ops_on
    row = c.row(align=True)
    user_list = f"PTDBLNPOPA_UL_{cname}"
    row.template_list(user_list, "", pool, cname, pool, iname, rows=2, maxrows=4)
    row = c.row(align=True)
    col = row.column(align=True)
    c_op = col.operator("ptdblnpopa.citem_enable", text="Disable" if boo else "Enable")
    c_op.cname = cname
    c_op.iname = iname
    c_op.doall = False
    col = row.column(align=True)
    c_op = col.operator("ptdblnpopa.citem_remove", text="Remove")
    c_op.cname = cname
    c_op.iname = iname
    c_op.doall = False
    col = row.column(align=True)
    col.enabled = coll_idx > 0
    c_op = col.operator("ptdblnpopa.citem_move", icon="TRIA_UP", text="")
    c_op.cname = cname
    c_op.iname = iname
    c_op.move_down = False
    row = c.row(align=True)
    col = row.column(align=True)
    col.enabled = len(coll_ob) > 1
    boo = False
    for i in coll_ob:
        if i.active:
            boo = True
            break
    c_op = col.operator(
        "ptdblnpopa.citem_enable",
        text="Disable All" if boo else "Enable All",
    )
    c_op.cname = cname
    c_op.iname = iname
    c_op.doall = True
    c_op.flagall = not boo
    col = row.column(align=True)
    col.enabled = len(coll_ob) > 1
    c_op = col.operator("ptdblnpopa.citem_remove", text="Remove All")
    c_op.cname = cname
    c_op.iname = iname
    c_op.doall = True
    col = row.column(align=True)
    col.enabled = coll_idx < (len(coll_ob) - 1)
    c_op = col.operator("ptdblnpopa.citem_move", icon="TRIA_DOWN", text="")
    c_op.cname = cname
    c_op.iname = iname
    c_op.move_down = True


def anim_rot_tmpl(c, ob):
    anirot = ob.ani_rot
    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(anirot, "active", toggle=True)
    col = row.column(align=True)
    col.enabled = anirot.active
    col.prop(anirot, "angle", text="")
    row = c.row(align=True)
    row.enabled = anirot.active
    row.prop(anirot, "beg", text="")
    row.prop(anirot, "end", text="")
    row = c.row(align=True)
    row.enabled = anirot.active
    row.prop(anirot, "lerp", text="factors", toggle=True)


def anim_ind_tmpl(c, ob, cap):
    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(ob, "active", toggle=True, text=cap)
    col = row.column(align=True)
    col.enabled = ob.active
    col.prop(ob, "offset", text="")
    row = c.row(align=True)
    row.enabled = ob.active
    col = row.column(align=True)
    col.prop(ob, "offrnd", toggle=True)
    col = row.column(align=True)
    col.enabled = ob.offrnd
    col.prop(ob, "offrndseed", text="")
    row = c.row(align=True)
    row.enabled = ob.active
    row.prop(ob, "beg", text="")
    row.prop(ob, "stp", text="")


def anim_fac_tmpl(c, ob):
    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(ob, "active", toggle=True)
    col = row.column(align=True)
    col.enabled = ob.active
    col.prop(ob, "fac", text="")
    row = c.row(align=True)
    row.enabled = ob.active
    col = row.column(align=True)
    col.prop(ob.mirror, "active", toggle=True)
    col = row.column(align=True)
    col.enabled = ob.mirror.active
    col.prop(ob.mirror, "cycles", text="")


def anim_fac_mirror_tmpl(c, flag, afm_ob):
    row = c.row(align=True)
    row.enabled = flag
    col = row.column(align=True)
    col.prop(afm_ob, "active", toggle=True)
    col = row.column(align=True)
    col.enabled = afm_ob.active
    col.prop(afm_ob, "cycles", text="")


class PTDBLNPOPA_PT_ui:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Apop"


class PTDBLNPOPA_PT_ui_setup(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Setup"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        pans_ok = ed_panels_ok(pool)
        base_ok = basels_ok(scene, pool)
        layout = self.layout
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.prop(pool, "sample_ob", text="")
        col = bcol.column(align=True)
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.enabled = base_ok and pans_ok
        rc.operator("ptdblnpopa.pop_reset", text="Load Current").newdef = False
        rc = row.column(align=True)
        rc.enabled = base_ok
        rc.operator("ptdblnpopa.pop_reset", text="Load Default").newdef = True
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.enabled = base_ok
        rc.operator("ptdblnpopa.read_setts", text="Load File")
        rc = row.column(align=True)
        rc.enabled = base_ok and pans_ok and not pool.animorph
        rc.operator("ptdblnpopa.write_setts", text="Save File")
        setcoll_ok = bool(pool.setcoll)
        row = col.row(align=True)
        row.enabled = setcoll_ok
        cap = pool.setcoll.name if setcoll_ok else "none"
        row.prop(pool, "replace_set", text=f'replace  "{cap}"', toggle=True)
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = base_ok and pans_ok and not pool.animorph
        dim2 = pool.use_profile
        cap = "2D Array" if dim2 else "Single Array"
        row.operator("ptdblnpopa.poparray_setup", text=cap).single = dim2
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.prop(pool, "show_warn", toggle=True)


class PTDBLNPOPA_PT_ui_path(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Path"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        base_ok = basels_ok(scene, pool)
        path = pool.path
        layout = self.layout
        path_rule = pool.prof.clean if pool.use_profile else True
        path_setup = base_ok and path_rule and not pool.animorph
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = path_setup
        col = row.column(align=True)
        col.prop(path, "provider", text="")
        col = row.column(align=True)
        provider = path.provider
        if provider == "custom":
            col.prop(path, "user_ob", text="")
        else:
            col.enabled = path.clean
            col.prop(path, f"res_{provider[:3]}", text="")
        path_edit = arrayset_ok(scene) and ed_panels_ok(pool)
        col = bcol.column(align=True)
        col.enabled = path_edit
        col.operator("ptdblnpopa.path_edit", text="Edit")
        pathed = path.pathed
        col = bcol.column(align=True)
        col.enabled = path_edit and not pool.animorph
        row = col.row(align=True)
        row.prop(pathed, "closed", toggle=True)
        row.prop(pathed, "idx", text="")
        path_att = pool.path_att
        col = bcol.column(align=True)
        col.enabled = path_edit
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.prop(path_att, "active", toggle=True)
        rc = row.column(align=True)
        rc.enabled = path_att.active
        rc.prop(path_att, "upfixed", toggle=True)
        row = col.row(align=True)
        row.enabled = path_att.active
        rc = row.column(align=True)
        rc.prop(path_att, "track", text="")
        rc = row.column(align=True)
        rc.enabled = path_att.upfixed
        rc.prop(path_att, "up", text="")
        row = col.row(align=True)
        row.enabled = False
        cap = f"nodes: {pathed.npts}" if path.clean else "... missing data!"
        row.label(text=cap)


class PTDBLNPOPA_PT_ui_path_anim(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPA_PT_ui_path"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        path = pool.path
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        provider = path.provider
        if provider == "line":
            dname = "length"
            dprop = "ani_lin_dim"
            fname = "exponent"
            fprop = "ani_lin_exp"
        elif provider == "wave":
            dname = "length"
            dprop = "ani_wav_dim"
            fname = "amplitude"
            fprop = "ani_wav_amp"
            fname2 = "frequency"
            fprop2 = "ani_wav_frq"
            fname3 = "phase"
            fprop3 = "ani_wav_pha"
        elif provider == "arc":
            dname = "chord"
            dprop = "ani_arc_dim"
            fname = "factor"
            fprop = "ani_arc_fac"
        elif provider == "helix":
            dname = "width"
            dprop = "ani_dim_2d"
            fname = "length"
            fprop = "ani_hel_len"
            fname2 = "factor"
            fprop2 = "ani_hel_fac"
            fname3 = "frequency"
            fprop3 = "ani_hel_stp"
            fname4 = "phase"
            fprop4 = "ani_hel_pha"
        elif provider == "spiral":
            dname = "diameter"
            dprop = "ani_spi_dim"
            fname = "frequency"
            fprop = "ani_spi_revs"
        elif provider == "torus":
            dname = "size"
            dprop = "ani_dim_2d"
            fname = "frequency"
            fprop = "ani_tor_stp"
            fname2 = "phase"
            fprop2 = "ani_tor_pha"
        else:
            dname = "size"
            dprop = "ani_dim_3d" if provider == "custom" else "ani_dim_2d"
        anim_ind_tmpl(c, path.ani_nidx, "index")
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(path, "ani_dim", toggle=True, text=dname)
        col = row.column(align=True)
        col.enabled = path.ani_dim
        row = col.row(align=True)
        if provider == "custom":
            for i in range(3):
                if path.pathed.user_dim[i]:
                    row.prop(path, dprop, index=i, text="")
        else:
            row.prop(path, dprop, text="")
        anim_fac_mirror_tmpl(c, path.ani_dim, path.ani_dim_mirror)
        if provider in {"line", "wave", "arc", "helix", "spiral", "torus"}:
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(path, "ani_fac", toggle=True, text=fname)
            col = row.column(align=True)
            col.enabled = path.ani_fac
            col.prop(path, fprop, text="")
            anim_fac_mirror_tmpl(c, path.ani_fac, path.ani_fac_mirror)
            if provider in {"wave", "helix", "torus"}:
                row = c.row(align=True)
                col = row.column(align=True)
                col.prop(path, "ani_fac2", toggle=True, text=fname2)
                col = row.column(align=True)
                col.enabled = path.ani_fac2
                col.prop(path, fprop2, text="")
                anim_fac_mirror_tmpl(c, path.ani_fac2, path.ani_fac2_mirror)
                if provider in {"wave", "helix"}:
                    row = c.row(align=True)
                    col = row.column(align=True)
                    col.prop(path, "ani_fac3", toggle=True, text=fname3)
                    col = row.column(align=True)
                    col.enabled = path.ani_fac3
                    col.prop(path, fprop3, text="")
                    anim_fac_mirror_tmpl(c, path.ani_fac3, path.ani_fac3_mirror)
                    if provider == "helix":
                        row = c.row(align=True)
                        col = row.column(align=True)
                        col.prop(path, "ani_fac4", toggle=True, text=fname4)
                        col = row.column(align=True)
                        col.enabled = path.ani_fac4
                        col.prop(path, fprop4, text="")
                        anim_fac_mirror_tmpl(c, path.ani_fac4, path.ani_fac4_mirror)


class PTDBLNPOPA_PT_ui_prof(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Profile"

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopa_pool.use_profile

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        base_ok = basels_ok(scene, pool)
        prof = pool.prof
        layout = self.layout
        prof_setup = base_ok and pool.path.clean and not pool.animorph
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = prof_setup
        col = row.column(align=True)
        col.prop(prof, "provider", text="")
        col = row.column(align=True)
        provider = prof.provider
        if provider == "custom":
            col.prop(prof, "user_ob", text="")
        else:
            col.enabled = prof.clean
            col.prop(prof, f"res_{provider[:3]}", text="")
        prof_edit = arrayset_ok(scene) and pool.prof.clean and pool.path.clean
        col = bcol.column(align=True)
        col.enabled = prof_edit
        col.operator("ptdblnpopa.prof_edit", text="Edit")
        profed = prof.profed
        col = bcol.column(align=True)
        col.enabled = prof_edit and not pool.animorph
        row = col.row(align=True)
        row.prop(profed, "closed", toggle=True)
        row.prop(profed, "idx", text="")
        prof_att = pool.prof_att
        col = bcol.column(align=True)
        col.enabled = prof_edit
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.prop(prof_att, "active", toggle=True)
        rc = row.column(align=True)
        rc.enabled = prof_att.active
        rc.prop(prof_att, "upfixed", toggle=True)
        row = col.row(align=True)
        row.enabled = prof_att.active
        rc = row.column(align=True)
        rc.prop(prof_att, "track", text="")
        rc = row.column(align=True)
        rc.enabled = prof_att.upfixed
        rc.prop(prof_att, "up", text="")
        col = bcol.column(align=True)
        col.enabled = prof_edit
        row = col.row(align=True)
        row.prop(pool, "full_att", toggle=True)
        row = col.row(align=True)
        row.enabled = False
        cap = f"points: {profed.npts}" if prof.clean else "... missing data!"
        row.label(text=cap)


class PTDBLNPOPA_PT_ui_prof_anim(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPA_PT_ui_prof"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        prof = pool.prof
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and pool.prof.clean and pool.path.clean
        box = layout.box()
        c = box.column(align=True)
        provider = prof.provider
        if provider == "line":
            dname = "length"
            dprop = "ani_lin_dim"
            fname = "exponent"
            fprop = "ani_lin_exp"
        elif provider == "wave":
            dname = "length"
            dprop = "ani_wav_dim"
            fname = "amplitude"
            fprop = "ani_wav_amp"
            fname2 = "frequency"
            fprop2 = "ani_wav_frq"
            fname3 = "phase"
            fprop3 = "ani_wav_pha"
        elif provider == "arc":
            dname = "chord"
            dprop = "ani_arc_dim"
            fname = "factor"
            fprop = "ani_arc_fac"
        else:
            dname = "size"
            dprop = "ani_epc_dim"
        anim_ind_tmpl(c, prof.ani_idx, "index")
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(prof, "ani_dim", toggle=True, text=dname)
        col = row.column(align=True)
        col.enabled = prof.ani_dim
        row = col.row(align=True)
        if provider == "custom":
            for i in range(2):
                if prof.profed.user_dim[i]:
                    row.prop(prof, dprop, index=i, text="")
        else:
            row.prop(prof, dprop, text="")
        anim_fac_mirror_tmpl(c, prof.ani_dim, prof.ani_dim_mirror)
        if provider in {"line", "wave", "arc"}:
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(prof, "ani_fac", toggle=True, text=fname)
            col = row.column(align=True)
            col.enabled = prof.ani_fac
            col.prop(prof, fprop, text="")
            anim_fac_mirror_tmpl(c, prof.ani_fac, prof.ani_fac_mirror)
            if provider == "wave":
                row = c.row(align=True)
                col = row.column(align=True)
                col.prop(prof, "ani_fac2", toggle=True, text=fname2)
                col = row.column(align=True)
                col.enabled = prof.ani_fac2
                col.prop(prof, fprop2, text="")
                anim_fac_mirror_tmpl(c, prof.ani_fac2, prof.ani_fac2_mirror)
                row = c.row(align=True)
                col = row.column(align=True)
                col.prop(prof, "ani_fac3", toggle=True, text=fname3)
                col = row.column(align=True)
                col.enabled = prof.ani_fac3
                col.prop(prof, fprop3, text="")
                anim_fac_mirror_tmpl(c, prof.ani_fac3, prof.ani_fac3_mirror)


class PTDBLNPOPA_PT_ui_pathloc(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Path Locations"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.pathloc
        collid = pool.pathloc_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "pathloc", "pathloc_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopa.pathloc_edit", text="Edit")
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPA_PT_ui_pathloc_anim(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPA_PT_ui_pathloc"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.pathloc:
            item = pool.pathloc[pool.pathloc_idx]
            c.enabled = item.active
            anim_ind_tmpl(c, item.ani_nidx, "node id")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPA_PT_ui_pathrot(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Path Rotations"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.pathrot
        collid = pool.pathrot_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "pathrot", "pathrot_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopa.pathrot_edit", text="Edit")
            c = bcol.column(align=True)
            c.enabled = item.active
            c.label(text="animation options")
            anim_rot_tmpl(c, item)
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPA_PT_ui_profloc(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Profile Locations"

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopa_pool.use_profile

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.profloc
        collid = pool.profloc_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "profloc", "profloc_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopa.profloc_edit", text="Edit")
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPA_PT_ui_profloc_anim(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPA_PT_ui_profloc"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.profloc:
            item = pool.profloc[pool.profloc_idx]
            c.enabled = item.active
            anim_ind_tmpl(c, item.ani_nidx, "node id")
            anim_ind_tmpl(c, item.ani_idx, "point id")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPA_PT_ui_profrot(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Profile Rotations"

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopa_pool.use_profile

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.profrot
        collid = pool.profrot_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "profrot", "profrot_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopa.profrot_edit", text="Edit")
            c = bcol.column(align=True)
            c.enabled = item.active
            c.label(text="animation options")
            anim_rot_tmpl(c, item)
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPA_PT_ui_noiz(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Noise Locations"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        noiz = pool.noiz
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator("ptdblnpopa.pop_noiz", text="Edit")
        row.prop(
            noiz,
            "active",
            text="",
            toggle=True,
            icon="CHECKMARK" if noiz.active else "PROP_OFF",
        )
        c = bcol.column(align=True)
        c.enabled = noiz.active
        c.label(text="animation options")
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(noiz, "ani_noiz", toggle=True)
        col = row.column(align=True)
        col.enabled = noiz.ani_noiz
        col.prop(noiz, "ani_seed", toggle=True)
        row = c.row(align=True)
        row.enabled = noiz.ani_noiz
        row.prop(noiz, "ani_blin", text="")
        row.prop(noiz, "ani_blout", text="")
        row.prop(noiz, "ani_stp", text="")


class PTDBLNPOPA_PT_ui_obloc(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Object Locations"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.obloc
        collid = pool.obloc_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "obloc", "obloc_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopa.obloc_edit", text="Edit")
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPA_PT_ui_obloc_anim(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPA_PT_ui_obloc"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.obloc:
            item = pool.obloc[pool.obloc_idx]
            c.enabled = item.active
            anim_ind_tmpl(c, item.ani_nidx, "node id")
            if pool.use_profile:
                anim_ind_tmpl(c, item.ani_idx, "point id")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPA_PT_ui_obrot(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Object Rotations"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.obrot
        collid = pool.obrot_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "obrot", "obrot_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopa.obrot_edit", text="Edit")
            c = bcol.column(align=True)
            c.enabled = item.active
            c.label(text="animation options")
            anim_rot_tmpl(c, item)
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPA_PT_ui_obsca(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Object Scales"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.obsca
        collid = pool.obsca_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "obsca", "obsca_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            col.enabled = item.active
            col.operator("ptdblnpopa.obsca_edit", text="Edit")
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPA_PT_ui_obsca_anim(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPA_PT_ui_obsca"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.obsca:
            item = pool.obsca[pool.obsca_idx]
            c.enabled = item.active
            anim_ind_tmpl(c, item.ani_nidx, "node id")
            if pool.use_profile:
                anim_ind_tmpl(c, item.ani_idx, "point id")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPA_PT_ui_ranges(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Object Range"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        rngs = pool.rngs
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool) and not pool.animorph
        box = layout.box()
        bcol = box.column()
        range_on = rngs.active
        cap = "Disable" if range_on else "Enable"
        row = bcol.row(align=True)
        col = row.column(align=True)
        col.operator("ptdblnpopa.obrange_react", text=cap).active = range_on
        col = row.column(align=True)
        col.enabled = range_on
        col.prop(rngs, "invert", toggle=True)
        row = bcol.row(align=True)
        row.enabled = range_on
        col = row.column(align=True)
        rc = col.row(align=True)
        rc.prop(rngs, "rbeg", text="")
        rc = col.row(align=True)
        rc.prop(rngs, "ritm", text="")
        rc = col.row(align=True)
        rc.prop(rngs, "rgap", text="")
        rc = col.row(align=True)
        rc.prop(rngs, "rstp", text="")
        if pool.use_profile:
            col = row.column(align=True)
            rc = col.row(align=True)
            rc.prop(rngs, "pbeg", text="")
            rc = col.row(align=True)
            rc.prop(rngs, "pitm", text="")
            rc = col.row(align=True)
            rc.prop(rngs, "pgap", text="")
            rc = col.row(align=True)
            rc.prop(rngs, "pstp", text="")
        row = bcol.row(align=True)
        row.enabled = range_on
        col = row.column(align=True)
        col.prop(rngs, "rndsel", toggle=True)
        col = row.column(align=True)
        col.enabled = rngs.rndsel
        col.prop(rngs, "nseed", text="")


class PTDBLNPOPA_PT_ui_utilities(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Utilities"

    def draw(self, context):
        pass


class PTDBLNPOPA_PT_ui_save_path_object(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Save Path Object"
    bl_parent_id = "PTDBLNPOPA_PT_ui_utilities"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = ed_panels_ok(pool)
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(pool, "custom_path_use_edits", toggle=True)
        row = col.row(align=True)
        row.operator("ptdblnpopa.custom_path_create", text="Create Path Object")


class PTDBLNPOPA_PT_ui_batchcoll_toggle(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Batch Toggle Edits"
    bl_parent_id = "PTDBLNPOPA_PT_ui_utilities"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        b_ops = pool.batchtoggle_ops
        layout = self.layout
        layout.enabled = arrayset_ok(context.scene) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator("ptdblnpopa.batchcoll_toggle", text="Clear Temp Flags").action = (
            "cleartemps"
        )
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.prop(b_ops, "path", toggle=True)
        prof_on = pool.use_profile
        if prof_on:
            row.prop(b_ops, "prof", toggle=True)
        row.prop(b_ops, "object", toggle=True)
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = b_ops.path or b_ops.object or (prof_on and b_ops.prof)
        row.operator("ptdblnpopa.batchcoll_toggle", text="Disable").action = "disable"
        row.operator("ptdblnpopa.batchcoll_toggle", text="Restore").action = "restore"
        row.operator("ptdblnpopa.batchcoll_toggle", text="Enable").action = "enable"


class PTDBLNPOPA_PT_ui_batchcoll_update(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Batch Update Edits"
    bl_parent_id = "PTDBLNPOPA_PT_ui_utilities"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        b_ops = pool.batchupdate_ops
        b_eds = b_ops.edits
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool) and not pool.animorph
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.prop(b_ops, "nodes", text="")
        prof_on = pool.use_profile
        if prof_on:
            row.prop(b_ops, "points", text="")
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.prop(b_eds, "path", toggle=True)
        if prof_on:
            row.prop(b_eds, "prof", toggle=True)
        row.prop(b_eds, "object", toggle=True)
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = b_eds.path or b_eds.object or (prof_on and b_eds.prof)
        row.operator("ptdblnpopa.batchcoll_update", text="Basic").doall = False
        row.operator("ptdblnpopa.batchcoll_update", text="Match").doall = True


class PTDBLNPOPA_PT_ui_anicalc(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Anicalc"
    bl_parent_id = "PTDBLNPOPA_PT_ui_utilities"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        clc = pool.anicalc
        layout = self.layout
        box = layout.box()
        bcol = box.column()
        row = bcol.row(align=True)
        c = row.column(align=True)
        c.operator("ptdblnpopa.anicalc", text="Calculate").current = False
        caller = clc.calc_type
        c = row.column(align=True)
        c.enabled = caller != "offsets"
        c.operator("ptdblnpopa.anicalc", text="Current").current = True
        row = bcol.row(align=True)
        row.prop(clc, "calc_type", text="")
        row = bcol.row(align=True)
        col = row.column(align=True)
        row = col.row(align=True)
        if caller == "loop":
            row.prop(clc, "items", text="")
            row.prop(clc, "offset", text="")
            row = col.row(align=True)
            row.prop(clc, "start", text="")
            row.prop(clc, "step", text="")
        elif caller == "offsets":
            row.prop(clc, "items", text="")
        elif caller == "cycles":
            row.prop(clc, "loop", text="")
        else:
            row.prop(clc, "fra", text="")
            row.prop(clc, "exp", text="")
            row = col.row(align=True)
            row.prop(clc, "first", text="")
            row.prop(clc, "last", text="")
        row = col.row(align=True)
        row.prop(clc, "info", text="")


class PTDBLNPOPA_PT_ui_animode(PTDBLNPOPA_PT_ui, bpy.types.Panel):
    bl_label = "Animation"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopa_pool
        layout = self.layout
        layout.enabled = arrayset_ok(scene) and ed_panels_ok(pool)
        animode_on = pool.animorph
        cap = "Leave Animode" if animode_on else "Enter Animode"
        box = layout.box()
        bcol = box.column()
        row = bcol.row()
        row.operator("ptdblnpopa.animorph_setup", text=cap).exiting = animode_on
        col = bcol.column(align=True)
        col.enabled = animode_on
        row = col.row(align=True)
        row.prop(pool, "act_name", text="")
        row.prop(pool, "ani_kf_type", text="")
        row = col.row(align=True)
        row.prop(pool, "act_loc", text="location", toggle=True)
        row.prop(pool, "act_rot", text="rotation", toggle=True)
        row.prop(pool, "act_sca", text="scale", toggle=True)
        col = bcol.column(align=True)
        col.enabled = animode_on
        row = col.row(align=True)
        row.prop(pool, "ani_kf_start", text="")
        row.prop(pool, "ani_kf_step", text="")
        row.prop(pool, "ani_kf_loop", text="")
        row = col.row(align=True)
        row.prop(pool, "shqu", toggle=True)
        row = col.row(align=True)
        row.operator("ptdblnpopa.anicycmirend")
        trax = pool.trax
        traxidx = pool.trax_idx
        nla_on = animode_on and bool(trax)
        col = bcol.column(align=True)
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.enabled = animode_on
        rc.operator("ptdblnpopa.anim_action", text="Add")
        rc = row.column(align=True)
        rc.enabled = nla_on
        rc.operator("ptdblnpopa.track_copy", text="Copy")
        col = col.column(align=True)
        col.enabled = nla_on
        row = col.row(align=True)
        row.template_list(
            "PTDBLNPOPA_UL_trax", "", pool, "trax", pool, "trax_idx", rows=2, maxrows=4
        )
        row = col.row(align=True)
        boo = trax[traxidx].active if nla_on else False
        c = row.column(align=True)
        c.operator(
            "ptdblnpopa.track_enable", text="Disable" if boo else "Enable"
        ).doall = False
        c = row.column(align=True)
        c.operator("ptdblnpopa.track_remove", text="Remove").doall = False
        row = col.row(align=True)
        c = row.column(align=True)
        boo = False
        for i in trax:
            if i.active:
                boo = True
                break
        c.enabled = len(trax) > 1
        trk_op = c.operator(
            "ptdblnpopa.track_enable", text="Disable All" if boo else "Enable All"
        )
        trk_op.doall = True
        trk_op.flagall = not boo
        c = row.column(align=True)
        c.enabled = len(trax) > 1
        c.operator("ptdblnpopa.track_remove", text="Remove All").doall = True
        c = col.column(align=True)
        if nla_on:
            item = trax[traxidx]
            row = c.row(align=True)
            row.enabled = item.active
            row.operator("ptdblnpopa.track_edit", text="Edit")
            box = c.box()
            box.enabled = False
            row = box.row(align=True)
            s = row.split(factor=0.6)
            sc = s.column(align=True)
            names = ("Action Range:", "Strip Frames:", "Scale:", "Repeat:")
            for n in names:
                row = sc.row(align=True)
                row.label(text=n)
            sc = s.column(align=True)
            row = sc.row(align=True)
            row.label(text=f"{item.sa_beg} - {item.sa_end}")
            row = sc.row(align=True)
            row.label(text=f"{item.s_beg} - {item.s_end}")
            row = sc.row(align=True)
            row.label(text=f"{item.s_sca:.4f}")
            row = sc.row(align=True)
            reps = 1.0 if item.st_warp else item.s_rep
            row.label(text=f"{reps:.4f}")
        else:
            c.enabled = False
            c.label(text="no tracks")


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------


classes = (
    PTDBLNPOPA_UL_pathloc,
    PTDBLNPOPA_UL_pathrot,
    PTDBLNPOPA_UL_profloc,
    PTDBLNPOPA_UL_profrot,
    PTDBLNPOPA_UL_obloc,
    PTDBLNPOPA_UL_obrot,
    PTDBLNPOPA_UL_obsca,
    PTDBLNPOPA_UL_trax,
    PTDBLNPOPA_PT_ui_setup,
    PTDBLNPOPA_PT_ui_path,
    PTDBLNPOPA_PT_ui_path_anim,
    PTDBLNPOPA_PT_ui_pathloc,
    PTDBLNPOPA_PT_ui_pathloc_anim,
    PTDBLNPOPA_PT_ui_pathrot,
    PTDBLNPOPA_PT_ui_prof,
    PTDBLNPOPA_PT_ui_prof_anim,
    PTDBLNPOPA_PT_ui_profloc,
    PTDBLNPOPA_PT_ui_profloc_anim,
    PTDBLNPOPA_PT_ui_profrot,
    PTDBLNPOPA_PT_ui_obloc,
    PTDBLNPOPA_PT_ui_obloc_anim,
    PTDBLNPOPA_PT_ui_obrot,
    PTDBLNPOPA_PT_ui_obsca,
    PTDBLNPOPA_PT_ui_obsca_anim,
    PTDBLNPOPA_PT_ui_noiz,
    PTDBLNPOPA_PT_ui_ranges,
    PTDBLNPOPA_PT_ui_utilities,
    PTDBLNPOPA_PT_ui_save_path_object,
    PTDBLNPOPA_PT_ui_batchcoll_toggle,
    PTDBLNPOPA_PT_ui_batchcoll_update,
    PTDBLNPOPA_PT_ui_anicalc,
    PTDBLNPOPA_PT_ui_animode,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
