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


    def button_search(self):
        self.ensure_one()
        query = self.search_query

        # Формування SQL запиту для виклику функції search_columns
        query_sql = sql.SQL("SELECT * FROM search_columns({query}, ARRAY['ir_module_module', 'account_account_template'])").format(query=sql.Literal(query))

        self.env.cr.execute(query_sql)
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
