from odoo import fields, models


class Skill(models.Model):
    _name = 'skill'

    name = fields.Char(string="Skill Name")
    level_ids = fields.One2many(
        comodel_name='skill.level',
        inverse_name='skill_id',
        string="Levels",
    )


class SkillLevel(models.Model):
    _name = 'skill.level'

    name = fields.Char(string="Level Name")
    skill_id = fields.Many2one(
        comodel_name='skill',
        string="Skill",
        ondelete='cascade',
    )


class EmployeeSkill(models.Model):
    _name = 'employee.skill'

    employee_id = fields.Many2one(
        comodel_name='employee',
        string="Employee",
        ondelete='cascade',
    )
    skill_id = fields.Many2one(
        comodel_name='skill',
        string="Skill",
        ondelete='cascade',
    )
    level_id = fields.Many2one(
        comodel_name='skill.level',
        string="Level",
        domain="[('skill_id', '=', skill_id)]",
        ondelete='set null',
    )