import logging

from odoo import models, fields, api
from psycopg2 import sql


class FullTextSearchResult(models.Model):
    _name = "full.text.search.result"
    _description = "Search Result"

    schemaname = fields.Char(string='Schema Name')
    tablename = fields.Char(string='Table Name')
    columnname = fields.Char(string='Column Name')
    rowctid = fields.Char(string='Row CTID')
    match_text = fields.Text(string='Match Text')
    search_id = fields.Many2one('full.text.search', string='Search Reference')

class FullTextSearch(models.Model):
    _name = "full.text.search"
    search_query = fields.Char(string='Search Query')
    search_results = fields.One2many('full.text.search.result', 'search_id', string='Results')

    selected_model_ids = fields.Many2many('ir.model', string='Select Models')

    @api.onchange('selected_model_ids')
    def _onchange_selected_model_ids(self):
        self.ensure_one()
        # Зберіть назви таблиць відповідно до вибраних моделей
        tables = self.selected_model_ids.mapped('model')
        # Ваш код для формування SQL запиту буде тут

    @api.model
    def _get_searchable_models(self):
        models_with_views = self.env['ir.ui.view'].search([('type', 'in', ('form', 'tree'))])
        return models_with_views.mapped('model_id')

    def get_table_name(self, model_name):
        # model_name - це технічне ім'я моделі, наприклад, 'res.partner'
        Model = self.env.get(model_name)
        return Model._table if Model else False

    def button_search(self):
        self.ensure_one()
        query = self.search_query.strip()

        # Перевірити, що пошуковий запит не пустий
        if not query:
            # Відобразити повідомлення про помилку або повернути з методу
            return

        # Отримати назви таблиць безпосередньо з об'єктів моделей
        tables_to_search = []
        for model in self.selected_model_ids:
            model_obj = self.env[model.model]
            if model_obj is not None:
                tables_to_search.append(model_obj._table)

        # Важливо: перевірити, що назви таблиць дійсно отримані
        if not tables_to_search:
            # Відобразити повідомлення про помилку або повернути з методу
            return

        # Формування масиву назв таблиць для SQL запиту
        formatted_tables = ','.join(["'%s'" % table for table in tables_to_search])

        # Формування і виконання SQL запиту
        query_sql = "SELECT * FROM search_columns(%s, ARRAY[{}]::name[])"
        formatted_query_sql = query_sql.format(formatted_tables)

        # Виконання SQL запиту з параметром пошуку
        self.env.cr.execute(formatted_query_sql, (query,))
        results = self.env.cr.fetchall()

        # Очистка попередніх результатів
        self.search_results.unlink()

        # Збереження нових результатів
        for result in results:
            self.search_results.create({
                'schemaname': result[0],
                'tablename': result[1],
                'columnname': result[2],
                'rowctid': result[3],
                'match_text': result[4],
                'search_id': self.id
            })




