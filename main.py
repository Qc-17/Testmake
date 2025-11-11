import os
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.snackbar import Snackbar
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock

from src.database import DatabaseManager
from src.pdf import PDFGenerator
from src.utils import QUESTION_TYPES, THEMES

import json


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        
        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        toolbar = MDTopAppBar(
            title="Verifica! - Home",
            md_bg_color=(0.09, 0.46, 0.82, 1)
        )
        layout.add_widget(toolbar)
        
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(10))
        
        welcome_label = MDLabel(
            text="Benvenuto in Verifica!",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )
        content.add_widget(welcome_label)
        
        desc_label = MDLabel(
            text="Gestisci le tue verifiche scolastiche in modo semplice e veloce",
            halign="center",
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(desc_label)
        
        content.add_widget(Widget(size_hint_y=0.1))
        
        btn_aggiungi = MDRaisedButton(
            text="Aggiungi Verifica",
            md_bg_color=(0.09, 0.46, 0.82, 1),
            size_hint=(0.8, None),
            height=dp(50),
            pos_hint={'center_x': 0.5},
            on_release=lambda x: self.manager.switch_to_screen('aggiungi')
        )
        content.add_widget(btn_aggiungi)
        
        btn_crea_pdf = MDRaisedButton(
            text="Crea PDF Verifiche",
            md_bg_color=(0.18, 0.49, 0.2, 1),
            size_hint=(0.8, None),
            height=dp(50),
            pos_hint={'center_x': 0.5},
            on_release=lambda x: self.manager.switch_to_screen('crea_pdf')
        )
        content.add_widget(btn_crea_pdf)
        
        btn_impostazioni = MDRaisedButton(
            text="Impostazioni",
            md_bg_color=(0.38, 0.38, 0.38, 1),
            size_hint=(0.8, None),
            height=dp(50),
            pos_hint={'center_x': 0.5},
            on_release=lambda x: self.manager.switch_to_screen('impostazioni')
        )
        content.add_widget(btn_impostazioni)
        
        content.add_widget(Widget(size_hint_y=0.3))
        
        layout.add_widget(content)
        self.add_widget(layout)


class AggiungiVerificaScreen(MDScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.name = 'aggiungi'
        self.db = db_manager
        self.current_verifica_id = None
        
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Aggiungi Verifica",
            md_bg_color=(0.09, 0.46, 0.82, 1),
            left_action_items=[["arrow-left", lambda x: self.manager.switch_to_screen('home')]]
        )
        layout.add_widget(toolbar)
        
        scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), adaptive_height=True)
        
        if self.current_verifica_id is None:
            self.titolo_field = MDTextField(
                hint_text="Titolo Verifica (es. Verifica su Hegel)",
                mode="rectangle",
                size_hint_y=None,
                height=dp(50)
            )
            content.add_widget(self.titolo_field)
            
            btn_crea = MDRaisedButton(
                text="Crea Verifica",
                md_bg_color=(0.09, 0.46, 0.82, 1),
                size_hint=(1, None),
                height=dp(50),
                on_release=self.crea_verifica
            )
            content.add_widget(btn_crea)
        else:
            verifica = self.db.get_verifica(self.current_verifica_id)
            content.add_widget(MDLabel(
                text=f"Verifica: {verifica['titolo']}", 
                font_style="H6",
                size_hint_y=None,
                height=dp(40)
            ))
            
            self.testo_domanda = MDTextField(
                hint_text="Testo della domanda",
                mode="rectangle",
                multiline=True,
                size_hint_y=None,
                height=dp(100)
            )
            content.add_widget(self.testo_domanda)
            
            self.risposta_domanda = MDTextField(
                hint_text="Risposta corretta (opzionale)",
                mode="rectangle",
                multiline=True,
                size_hint_y=None,
                height=dp(80)
            )
            content.add_widget(self.risposta_domanda)
            
            content.add_widget(MDLabel(
                text="Tipo di domanda:",
                size_hint_y=None,
                height=dp(30)
            ))
            
            self.selected_tipo = 'scelta_multipla'
            tipo_layout = MDBoxLayout(orientation='vertical', spacing=dp(5), adaptive_height=True)
            for tipo_key, tipo_label in QUESTION_TYPES:
                btn = MDRaisedButton(
                    text=tipo_label,
                    md_bg_color=(0.09, 0.46, 0.82, 1) if tipo_key == self.selected_tipo else (0.7, 0.7, 0.7, 1),
                    size_hint=(1, None),
                    height=dp(40),
                    on_release=lambda x, t=tipo_key: self.seleziona_tipo(t)
                )
                btn.tipo_key = tipo_key
                tipo_layout.add_widget(btn)
                setattr(self, f'btn_tipo_{tipo_key}', btn)
            content.add_widget(tipo_layout)
            
            content.add_widget(MDLabel(
                text="Difficoltà (1-10):",
                size_hint_y=None,
                height=dp(30)
            ))
            
            self.difficolta_field = MDTextField(
                hint_text="5",
                text="5",
                mode="rectangle",
                input_filter="int",
                size_hint_y=None,
                height=dp(50)
            )
            content.add_widget(self.difficolta_field)
            
            btn_aggiungi_domanda = MDRaisedButton(
                text="Aggiungi Domanda",
                md_bg_color=(0.18, 0.49, 0.2, 1),
                size_hint=(1, None),
                height=dp(50),
                on_release=self.aggiungi_domanda
            )
            content.add_widget(btn_aggiungi_domanda)
            
            domande = self.db.get_domande_by_verifica(self.current_verifica_id)
            if domande:
                content.add_widget(MDLabel(
                    text=f"Domande aggiunte: {len(domande)}",
                    font_style="H6",
                    size_hint_y=None,
                    height=dp(40)
                ))
                
                for idx, d in enumerate(domande, 1):
                    tipo_label = dict(QUESTION_TYPES).get(d['tipo'], d['tipo'])
                    item_text = f"{idx}. [{tipo_label}] {d['testo'][:50]}..."
                    content.add_widget(OneLineListItem(
                        text=item_text,
                        on_release=lambda x: None
                    ))
            
            btn_visualizza_risposte = MDRaisedButton(
                text="Visualizza Risposte",
                md_bg_color=(0.38, 0.38, 0.38, 1),
                size_hint=(1, None),
                height=dp(50),
                on_release=self.visualizza_risposte
            )
            content.add_widget(btn_visualizza_risposte)
            
            btn_nuova = MDRaisedButton(
                text="Crea Nuova Verifica",
                md_bg_color=(0.09, 0.46, 0.82, 1),
                size_hint=(1, None),
                height=dp(50),
                on_release=self.nuova_verifica
            )
            content.add_widget(btn_nuova)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def seleziona_tipo(self, tipo):
        self.selected_tipo = tipo
        for tipo_key, _ in QUESTION_TYPES:
            btn = getattr(self, f'btn_tipo_{tipo_key}', None)
            if btn:
                btn.md_bg_color = (0.09, 0.46, 0.82, 1) if tipo_key == tipo else (0.7, 0.7, 0.7, 1)
    
    def crea_verifica(self, instance):
        titolo = self.titolo_field.text.strip()
        if not titolo:
            Snackbar(text="Inserisci un titolo per la verifica!").open()
            return
        
        self.current_verifica_id = self.db.add_verifica(titolo)
        Snackbar(text=f"Verifica '{titolo}' creata!").open()
        self.build_ui()
    
    def aggiungi_domanda(self, instance):
        testo = self.testo_domanda.text.strip()
        if not testo:
            Snackbar(text="Inserisci il testo della domanda!").open()
            return
        
        risposta = self.risposta_domanda.text.strip()
        
        try:
            difficolta = int(self.difficolta_field.text or "5")
            difficolta = max(1, min(10, difficolta))
        except:
            difficolta = 5
        
        self.db.add_domanda(self.current_verifica_id, testo, risposta, self.selected_tipo, difficolta)
        Snackbar(text="Domanda aggiunta con successo!").open()
        
        self.testo_domanda.text = ""
        self.risposta_domanda.text = ""
        self.difficolta_field.text = "5"
        
        self.build_ui()
    
    def visualizza_risposte(self, instance):
        self.manager.get_screen('risposte').set_verifica(self.current_verifica_id)
        self.manager.switch_to_screen('risposte')
    
    def nuova_verifica(self, instance):
        self.current_verifica_id = None
        self.build_ui()


class VisualizzaRisposteScreen(MDScreen):
    def __init__(self, db_manager, pdf_gen, **kwargs):
        super().__init__(**kwargs)
        self.name = 'risposte'
        self.db = db_manager
        self.pdf_gen = pdf_gen
        self.verifica_id = None
        
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Visualizza Risposte",
            md_bg_color=(0.09, 0.46, 0.82, 1),
            left_action_items=[["arrow-left", lambda x: self.manager.switch_to_screen('aggiungi')]]
        )
        layout.add_widget(toolbar)
        
        scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), adaptive_height=True)
        
        if self.verifica_id:
            verifica = self.db.get_verifica(self.verifica_id)
            domande = self.db.get_domande_by_verifica(self.verifica_id)
            
            content.add_widget(MDLabel(
                text=f"Risposte: {verifica['titolo']}",
                font_style="H6",
                size_hint_y=None,
                height=dp(40)
            ))
            
            for idx, d in enumerate(domande, 1):
                tipo_label = dict(QUESTION_TYPES).get(d['tipo'], d['tipo'])
                domanda_text = f"{idx}. [{tipo_label}] Diff: {d['difficolta']}/10\n{d['testo']}"
                risposta_text = f"Risposta: {d['risposta'] or 'Non specificata'}"
                
                content.add_widget(MDLabel(
                    text=domanda_text,
                    size_hint_y=None,
                    height=dp(60)
                ))
                content.add_widget(MDLabel(
                    text=risposta_text,
                    theme_text_color="Custom",
                    text_color=(0.18, 0.49, 0.2, 1),
                    size_hint_y=None,
                    height=dp(30)
                ))
                content.add_widget(Widget(size_hint_y=None, height=dp(10)))
            
            btn_export = MDRaisedButton(
                text="Esporta PDF Risposte",
                md_bg_color=(0.18, 0.49, 0.2, 1),
                size_hint=(1, None),
                height=dp(50),
                on_release=self.export_pdf
            )
            content.add_widget(btn_export)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def set_verifica(self, verifica_id):
        self.verifica_id = verifica_id
        self.build_ui()
    
    def export_pdf(self, instance):
        if not self.verifica_id:
            return
        
        verifica = self.db.get_verifica(self.verifica_id)
        domande = self.db.get_domande_by_verifica(self.verifica_id)
        
        filename = f"risposte_{verifica['titolo'].replace(' ', '_')}.pdf"
        self.pdf_gen.genera_risposte_pdf(filename, verifica['titolo'], domande)
        Snackbar(text=f"PDF risposte salvato: {filename}").open()


class CreaPDFScreen(MDScreen):
    def __init__(self, db_manager, pdf_gen, **kwargs):
        super().__init__(**kwargs)
        self.name = 'crea_pdf'
        self.db = db_manager
        self.pdf_gen = pdf_gen
        
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Crea PDF Verifiche",
            md_bg_color=(0.09, 0.46, 0.82, 1),
            left_action_items=[["arrow-left", lambda x: self.manager.switch_to_screen('home')]]
        )
        layout.add_widget(toolbar)
        
        scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), adaptive_height=True)
        
        content.add_widget(MDLabel(
            text="Genera Verifiche Casuali",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        ))
        
        self.titolo_pdf = MDTextField(
            hint_text="Titolo della verifica",
            mode="rectangle",
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(self.titolo_pdf)
        
        self.num_alunni = MDTextField(
            hint_text="Numero di alunni",
            text="1",
            mode="rectangle",
            input_filter="int",
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(self.num_alunni)
        
        content.add_widget(MDLabel(
            text="Numero di domande per tipo:",
            size_hint_y=None,
            height=dp(30)
        ))
        
        self.tipo_fields = {}
        for tipo_key, tipo_label in QUESTION_TYPES:
            tipo_layout = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
            tipo_layout.add_widget(MDLabel(
                text=tipo_label,
                size_hint_x=0.7
            ))
            field = MDTextField(
                hint_text="0",
                text="0",
                mode="rectangle",
                input_filter="int",
                size_hint_x=0.3,
                size_hint_y=None,
                height=dp(50)
            )
            self.tipo_fields[tipo_key] = field
            tipo_layout.add_widget(field)
            content.add_widget(tipo_layout)
        
        btn_genera = MDRaisedButton(
            text="Genera PDF",
            md_bg_color=(0.18, 0.49, 0.2, 1),
            size_hint=(1, None),
            height=dp(50),
            on_release=self.genera_pdf
        )
        content.add_widget(btn_genera)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def genera_pdf(self, instance):
        titolo = self.titolo_pdf.text.strip()
        if not titolo:
            Snackbar(text="Inserisci un titolo per la verifica!").open()
            return
        
        try:
            num_alunni = int(self.num_alunni.text or "1")
            num_alunni = max(1, num_alunni)
        except:
            num_alunni = 1
        
        richieste = {}
        for tipo_key, field in self.tipo_fields.items():
            try:
                num = int(field.text or "0")
                if num > 0:
                    richieste[tipo_key] = num
            except:
                pass
        
        if not richieste:
            Snackbar(text="Seleziona almeno un tipo di domanda!").open()
            return
        
        domande = self.pdf_gen.seleziona_domande_casuali(self.db, richieste)
        
        if not domande:
            Snackbar(text="Non ci sono abbastanza domande disponibili!").open()
            return
        
        filename = f"verifiche_{titolo.replace(' ', '_')}.pdf"
        self.pdf_gen.genera_verifica_pdf(filename, titolo, domande, num_alunni)
        Snackbar(text=f"PDF generato: {filename}").open()


class ImpostazioniScreen(MDScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.name = 'impostazioni'
        self.db = db_manager
        
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Impostazioni",
            md_bg_color=(0.09, 0.46, 0.82, 1),
            left_action_items=[["arrow-left", lambda x: self.manager.switch_to_screen('home')]]
        )
        layout.add_widget(toolbar)
        
        scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), adaptive_height=True)
        
        content.add_widget(MDLabel(
            text="Impostazioni",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        ))
        
        tema_attuale = self.db.get_setting('tema') or 'chiaro'
        btn_tema = MDRaisedButton(
            text=f"Tema: {tema_attuale.title()}",
            md_bg_color=(0.09, 0.46, 0.82, 1),
            size_hint=(1, None),
            height=dp(50),
            on_release=self.cambia_tema
        )
        content.add_widget(btn_tema)
        
        btn_export = MDRaisedButton(
            text="Esporta Archivio",
            md_bg_color=(0.18, 0.49, 0.2, 1),
            size_hint=(1, None),
            height=dp(50),
            on_release=self.export_archivio
        )
        content.add_widget(btn_export)
        
        btn_import = MDRaisedButton(
            text="Importa Archivio",
            md_bg_color=(0.38, 0.38, 0.38, 1),
            size_hint=(1, None),
            height=dp(50),
            on_release=self.import_archivio
        )
        content.add_widget(btn_import)
        
        btn_reset = MDRaisedButton(
            text="Ripristina Impostazioni",
            md_bg_color=(0.8, 0.2, 0.2, 1),
            size_hint=(1, None),
            height=dp(50),
            on_release=self.reset_impostazioni
        )
        content.add_widget(btn_reset)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def cambia_tema(self, instance):
        tema_attuale = self.db.get_setting('tema') or 'chiaro'
        nuovo_tema = 'scuro' if tema_attuale == 'chiaro' else 'chiaro'
        self.db.set_setting('tema', nuovo_tema)
        
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = THEMES[nuovo_tema]
        
        self.build_ui()
    
    def export_archivio(self, instance):
        data = self.db.export_archivio()
        filename = f"archivio_verifica.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        Snackbar(text="Archivio esportato con successo!").open()
    
    def import_archivio(self, instance):
        try:
            filename = "archivio_verifica.json"
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.db.import_archivio(data)
                Snackbar(text="Archivio importato con successo!").open()
            else:
                Snackbar(text="File archivio non trovato!").open()
        except Exception as e:
            Snackbar(text="Errore durante l'importazione!").open()
    
    def reset_impostazioni(self, instance):
        self.db.set_setting('tema', 'chiaro')
        self.db.set_setting('formato_data', 'DD/MM/YYYY')
        self.db.set_setting('lingua', 'italiano')
        
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = 'Light'
        
        Snackbar(text="Impostazioni ripristinate!").open()
        self.build_ui()


class CustomScreenManager(MDScreenManager):
    def switch_to_screen(self, screen_name):
        self.current = screen_name


class VerificaApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        self.db = DatabaseManager()
        self.pdf_gen = PDFGenerator()
        
        tema = self.db.get_setting('tema') or 'chiaro'
        self.theme_cls.theme_style = THEMES[tema]
        
        Window.size = (400, 700)
        
        sm = CustomScreenManager()
        sm.add_widget(HomeScreen())
        sm.add_widget(AggiungiVerificaScreen(self.db))
        sm.add_widget(VisualizzaRisposteScreen(self.db, self.pdf_gen))
        sm.add_widget(CreaPDFScreen(self.db, self.pdf_gen))
        sm.add_widget(ImpostazioniScreen(self.db))
        
        return sm
    
    def on_stop(self):
        self.db.close()
        return True


if __name__ == '__main__':
    VerificaApp().run()
