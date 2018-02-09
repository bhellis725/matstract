import dash_html_components as html
import dash_core_components as dcc

from matstract.web.utils import open_db_connection

from chemdataextractor.doc import Paragraph
from chemdataextractor import Document


db = open_db_connection()


def serve_layout():
    """Generates the layout dynamically on every refresh"""
    return html.Div(serve_abstract(), id="annotation_container")


def serve_abstract():
    """Returns a random abstract and refreshes annotation options"""
    # get a random paragraph
    random_abstract = db.abstracts_vahe.aggregate([{"$sample": {"size": 1}}]).next()

    # tokenize using chemdataextractor
    # title
    ttl_tokens = Paragraph(random_abstract["title"]).tokens
    ttl_cems = Document(random_abstract["title"]).cems
    # abstract
    abs_tokens = Paragraph(random_abstract["abstract"]).tokens
    abs_cems = Document(random_abstract["abstract"]).cems

    return [
        html.Div(serve_labels(), id="label_container"),
        html.H5(build_tokens_html(ttl_tokens, ttl_cems), id="title_container", className="row"),
        html.Div(build_tokens_html(abs_tokens, abs_cems), id="abstract_container", className="row"),
        html.Div(serve_macro_annotation(), id="macro_annotation_container"),
        # html.Div(list_cde_cems(abs_cems), id='token_container'),
        html.Div(serve_buttons(), id="buttons_container", className="row")
    ]


def serve_macro_annotation():
    return [html.Div([html.Div("Type: ", className='two columns'),
            html.Div(dcc.Dropdown(
                options=[
                    {'label': 'Experimental', 'value': 'experimental'},
                    {'label': 'Theoretical', 'value': 'theoretical'},
                    {'label': 'Both', 'value': 'both'},
                    {'label': 'Unclear', 'value': 'unclear'},

                ],
                value='experimental',
                clearable=False,
                id='abstract_type'
            ), className='five columns',
            ), html.Div(dcc.Dropdown(
                options=[
                    {'label': 'Inorganic Crystals', 'value': 'inorganic'},
                    {'label': 'Other Materials', 'value': 'other_materials'},
                    {'label': 'Not Materials', 'value': 'not_materials'},
                ],
                value='inorganic',
                clearable=False,
                id='abstract_category'
            ), className='five columns',
            )], className='row'),
            html.Div([html.Div("Applications: ", className="two columns"),
                     html.Div(dcc.Dropdown(
                         options = [
                             {'label': 'Thermoelectric', 'value': 'thermoelectric'},
                             {'label': 'Battery', 'value': 'battery'},
                             {'label': 'Magnetic', 'value': 'magnetic'},
                             {'label': 'Other', 'value': 'other'}
                         ],
                         value='',
                         id='abstract_tags',
                         multi=True
                     ), className="ten columns")],
                     className="row")]


def build_tokens_html(tokens, cems):
    cde_cem_starts = [cem.start for cem in cems]
    """builds the HTML for tokenized paragraph"""
    html_builder = []
    for row in tokens:
        for elem in row:
            extra_class = ''
            if elem.start in cde_cem_starts:
                extra_class = " highlighted mtl"
            html_builder.append(" ")
            html_builder.append(html.Span(
                elem.text,
                id="abs-token-" + str(elem.start) + '-' + str(elem.end),
                className="abs-token" + extra_class,
            ))
    return html_builder


# def list_cde_cems(cems):
#     html_builder = []
#     for cem in cems:
#         html_builder.append(html.Div([
#             html.Div(
#                 cem.text,
#                 id="cde-cem-" + str(cem.start) + '-' + str(cem.end),
#                 className="six columns",
#             ), html.Div(dcc.Dropdown(
#                 options=[
#                     {'label': 'Material', 'value': 'mtl'},
#                     {'label': 'Inorganic Crystal', 'value': 'igc'},
#                 ],
#                 value='mtl',
#                 ),
#                 className="six columns",
#             )],
#             className="row",
#         ))
#     return html_builder


def serve_buttons():
    return [html.Button("Skip", id="annotate_skip", className="button"),
            html.Button("Confirm Annotation", id="annotate_confirm", className="button-primary")]


def serve_labels():
    return html.Div([
        html.Div(html.Span("Labels: "), className="two columns"),
        html.Div([
            html.Span("Material", className="highlighted mtl label"),
            html.Span("Inorganic Crystal", className="highlighted inrg label"),
            html.Span("Main Material", className="highlighted main_mtl label"),
            html.Br(),
            html.Span("Property Name", className="highlighted prop_name label"),
            html.Span("Property Value", className="highlighted prop_val label"),
            html.Span("Property Unit", className="highlighted prop_unit label")]
            , className="ten columns")], className="row")