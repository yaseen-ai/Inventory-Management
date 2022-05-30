import codecs
import yaml
import locale
import argparse

from pybars import Compiler

from weasyprint import HTML


parser = argparse.ArgumentParser(description='Convert HTML template to pdf with data from yaml')
parser.add_argument('--template', help='The name of the template to use (e.g. invoice)', default="invoice")
parser.add_argument('--yaml_file', help='The yaml file to use for data', default="documents/invoice/data.yml", type=str)
parser.add_argument('--output_pdf', help='The output pdf file', default="pdf.pdf", type=str)
parser.add_argument('--locale', help='The locale to use', default="en_US.UTF-8")
args = parser.parse_args()
locale.setlocale(locale.LC_ALL, args.locale)
document_url = 'documents/'+args.template
base_url = document_url+'/template'
index_html = base_url+'/index.html'
with open(args.yaml_file) as file:
    document_data = yaml.load(file, Loader=yaml.FullLoader)
pos_number = 1
document_data['totals'] = {
    'netto' : 0,
    'brutto': 0,
    'tax': 0        
}
for pos in document_data['positions']:
    if not 'tax_rate' in pos:
        #pos['tax_rate'] = document_data['tax_rate']
        pos['tax_rate'] = float(0)
    pos['pos_number'] = pos['ref']
    pos['total_netto_price'] = float(int(float(pos['netto_price'])) * int(float(pos['amount'])))
    pos['total_tax'] = float(pos['total_netto_price']) * (float(pos['tax_rate']) / float(100))
    pos['total_brutto_price'] = pos['total_netto_price'] + pos['total_tax']
    document_data['totals']['netto'] += pos['total_netto_price']
    document_data['totals']['brutto'] += pos['total_brutto_price']
    document_data['totals']['tax'] += pos['total_tax']
    pos['amount'] = locale.format_string("%.2f", int(float(pos['amount'])))
    pos['tax_rate'] = locale.format_string("%.2f", float(pos['tax_rate']))
    pos['netto_price'] = locale.format_string("%.2f", float(pos['netto_price']))
    pos['total_netto_price'] = locale.format_string("%.2f", pos['total_netto_price'])
    pos['text'] = pos['text'].replace('\n', '<br>')
    pos_number += 1
document_data['totals']['netto'] = locale.format_string("%.2f", document_data['totals']['netto'])
document_data['totals']['brutto'] = locale.format_string("%.2f", document_data['totals']['brutto'])
document_data['totals']['tax'] = locale.format_string("%.2f", document_data['totals']['tax'])
with codecs.open(index_html, encoding="utf-8") as index_file:
    html_text = index_file.read()
    
    compiler = Compiler()
    template = compiler.compile(html_text)
    
    html_text = template(document_data)
    weasytemplate = HTML(string=html_text, base_url=base_url)
    weasytemplate.write_pdf(args.output_pdf)
        
