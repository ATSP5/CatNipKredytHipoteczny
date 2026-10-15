# CatNip Interactive Report — generated from the block's page (markup, Python, style).
# Edit it in the block's editor: this file is rewritten whenever the editor is saved.
import base64 as _ir_base64
import html as _ir_html
import io as _ir_io
import json as _ir_json_module
import math as _ir_math
import os as _ir_os
import sys as _ir_sys
import threading as _ir_threading
import traceback as _ir_traceback
import uuid as _ir_uuid
import re
from datetime import datetime
from MortgageParameters import MortgageParameters
from MortgageReportSnapshot import MortgageReportSnapshot
from ReportTable import ReportTable


class AnalizaKredytuHipotecznego:
    TITLE = 'Kredyt hipoteczny na budowę domu'
    HEIGHT = 1100
    KEEP_ALIVE = True
    ACTIONS = {'zapisz': 'live'}
    CATNIP_LIVE_ACTIONS = ('zapisz', )
    MARKUP = (
        '<div class="cn-page">\n'
        '  <h1>Kredyt hipoteczny na budowę domu</h1>\n'
        '  <p class="cn-muted">Dochody gospodarstwa i plan budowy pochodzą z pliku <b>{household_file}</b> (wybieranego blokiem File content), oferty banków z <b>input/oferty_bankow.xlsx</b>. Wszystko poniżej możesz zmienić ręcznie — analiza przelicza się od razu, a przyciski „Przywróć” wracają do danych z plików.</p>\n'
        '  <p class="status small">{status_line}</p>\n'
        '\n'
        '  <div class="cn-row">\n'
        '    {button("Zapisz PDF", action="zapisz", disabled=not valid)}\n'
        '    {button("Wybierz najkorzystniejszy bank", call="use_best_offer", kind="secondary")}\n'
        '  </div>\n'
        '\n'
        '  {message_box}\n'
        '\n'
        '  <div class="cn-grid-4">{kpis if valid else ""}</div>\n'
        '\n'
        '  <div class="cn-grid-3">\n'
        '    <div class="cn-card">\n'
        '      <h3>Budowa i wkład własny</h3>\n'
        '      {number("house_cost", min=0, step=10000, label="Koszt budowy domu [zł]")}\n'
        '      {number("plot_value", min=0, step=10000, label="Wartość działki [zł]")}\n'
        '      {number("savings", min=0, step=5000, label="Oszczędności wkładane w budowę [zł]")}\n'
        '      <p class="small">Kwota kredytu: <b>{loan_amount}</b> · wkład własny: {own_contribution}</p>\n'
        '      {slider("build_months", 3, 36, step=1, label="Czas budowy [miesiące]", format=".0f")}\n'
        '      {slider("tranches", 1, 8, step=1, label="Liczba transz", format=".0f")}\n'
        '      <div class="cn-row">{button("Przywróć plan z Excela", call="reset_project", kind="secondary")}</div>\n'
        '    </div>\n'
        '    <div class="cn-card">\n'
        '      <h3>Kredyt i bank</h3>\n'
        '      {select("bank", bank_options, label="Bank (ustawia parametry oferty)")}\n'
        '      {slider("years", 5, 35, step=1, label="Okres kredytu [lata]", format=".0f")}\n'
        '      {radio("installment_type", [("równe", "Równe"), ("malejące", "Malejące")], label="Raty")}\n'
        '      {radio("rate_type", [("zmienna", "Zmienne: wskaźnik + marża"), ("stała", "Okresowo stałe")], label="Oprocentowanie")}\n'
        '      {select("index_name", index_options, label="Wskaźnik (WIBOR / POLSTR)") if rate_type == "zmienna" else ""}\n'
        '      {number("index_rate_pct", min=0, step=0.01, label="Wartość wskaźnika [%]") if rate_type == "zmienna" else ""}\n'
        '      {number("margin_pct", min=0, step=0.05, label="Marża banku [%]") if rate_type == "zmienna" else ""}\n'
        '      {number("fixed_rate_pct", min=0, step=0.05, label="Stała stopa z oferty banku [%]") if rate_type == "stała" else ""}\n'
        '      {number("commission_pct", min=0, step=0.1, label="Prowizja [%]")}\n'
        '      {number("bridge_margin_pp", min=0, step=0.1, label="Podwyżka do wpisu hipoteki [pp]")}\n'
        '      {slider("bridge_months", 0, 12, step=1, label="Miesiące do wpisu hipoteki", format=".0f")}\n'
        '      {number("property_insurance_pct", min=0, step=0.01, label="Ubezpieczenie nieruchomości [% rocznie]")}\n'
        '      <div class="cn-row">{button("Przywróć ofertę banku", call="reset_offer", kind="secondary")}</div>\n'
        '    </div>\n'
        '    <div class="cn-card">\n'
        '      <h3>Budżet rodziny</h3>\n'
        '      {budget_controls}\n'
        '      <div class="cn-row">{button("Przywróć dane z Excela", call="reset_budget", kind="secondary")}</div>\n'
        '    </div>\n'
        '  </div>\n'
        '\n'
        '  {html(\'<h2>Dochód z działalności (B2B)</h2><p class="cn-muted small">Arkusz Dochody podaje kwoty z faktur (netto, bez VAT). Bank i budżet liczą to, co zostaje po kosztach, ZUS społecznym, składce zdrowotnej i PIT — średnio z 12 miesięcy, stawki na 2026 r. Kwotę z faktury zmienisz w karcie Budżet rodziny — dochód na rękę i ta tabela przeliczą się same; formę opodatkowania, ZUS i koszty — w arkuszu Domownicy.</p>\') if business_rows else ""}\n'
        '  {table(business_rows, page_size=10, filter=False, sortable=False, formats={"Faktury [zł]": ",.0f", "Koszty [zł]": ",.0f", "ZUS społeczny [zł]": ",.0f", "Zdrowotna [zł]": ",.0f", "PIT [zł]": ",.0f", "Na rękę [zł]": ",.0f"}) if business_rows else ""}\n'
        '\n'
        '  <h2>Porównanie banków</h2>\n'
        '  <p class="cn-muted small">Każda oferta policzona dla tego samego planu budowy i okresu. Kliknij wiersz, aby przejść na ofertę banku.</p>\n'
        '  {table(comparison_rows, page_size=10, filter=False, select="chosen_offer", formats={"Marża [%]": ",.2f", "Prowizja [%]": ",.2f", "Oproc. [%]": ",.2f", "Rata po budowie [zł]": ",.0f", "Koszt całkowity [zł]": ",.0f", "RRSO [%]": ",.2f"}) if valid else ""}\n'
        '\n'
        '  <div class="cn-grid-2">\n'
        '    {plotly(comparison_chart) if valid else ""}\n'
        '    <div>\n'
        '      <h3>Ocena zdolności kredytowej</h3>\n'
        '      {table(assessment_rows, page_size=20, filter=False, sortable=False) if valid else ""}\n'
        '      {color_bar(dsti, 0, 70, label="DSTI przy teście stopy (limit " + str(round(dsti_limit)) + "%)", format=".1f") if valid else ""}\n'
        '    </div>\n'
        '  </div>\n'
        '\n'
        '  <div class="cn-grid-2">\n'
        '    {plotly(budget_chart) if valid else ""}\n'
        '    {chart("donut", cost_rows, labels="Składnik", values="zł", title="Struktura całkowitego kosztu", height=380) if valid else ""}\n'
        '  </div>\n'
        '\n'
        '  {plotly(payment_chart) if valid else ""}\n'
        '\n'
        '  <h2>Harmonogram spłat</h2>\n'
        '  {table(harmonogram, page_size=12, formats={"Transza": ",.2f", "Kapitał": ",.2f", "Odsetki": ",.2f", "Ubezpieczenie": ",.2f", "Rata łącznie": ",.2f", "Oproc. [%]": ",.2f", "Saldo": ",.2f"}) if valid else ""}\n'
        '\n'
        '  <p class="cn-muted small">Zdolność liczona uproszczonymi regułami Rekomendacji S KNF: rata przy oprocentowaniu powiększonym o bufor, limit DSTI zależny od dochodu, koszty życia nie niższe niż minimum na osobę, maksymalne LTV banku. Marże i prowizje są orientacyjne (publiczne rankingi) — wiążącą ofertę i decyzję kredytową daje bank.</p>\n'
        '</div>\n'
        ''
    )
    STYLE = (
        'h1 { color: #1f3b73; margin-bottom: 2px; }\n'
        'h2 { margin: 20px 0 6px; font-size: 1.1em; color: #1f3b73; }\n'
        'h3 { margin: 0 0 6px; font-size: 1em; }\n'
        'h4 { margin: 10px 0 4px; font-size: 0.9em; color: var(--cn-text2, #555); }\n'
        '.small { font-size: 0.85em; }\n'
        '.status { background: color-mix(in srgb, var(--cn-accent) 8%, transparent); border-radius: var(--cn-radius); padding: 6px 10px; }\n'
        '.msg { border-radius: var(--cn-radius); padding: 7px 12px; margin: 6px 0; border-left: 4px solid; }\n'
        '.msg.ok { background: color-mix(in srgb, #27ae60 12%, transparent); border-color: #27ae60; }\n'
        '.msg.warning { background: color-mix(in srgb, var(--cn-warning, #e67e22) 14%, transparent); border-color: var(--cn-warning, #e67e22); }\n'
        '.msg.error { background: color-mix(in srgb, var(--cn-bad, #c0392b) 12%, transparent); border-color: var(--cn-bad, #c0392b); }\n'
        '.cn-kpi.bad { border-top-color: var(--cn-bad); }\n'
        '.cn-kpi.bad .cn-kpi-value { color: var(--cn-bad); }\n'
        '.cn-kpi-value { font-size: 1.3em; }\n'
        ''
    )

    def __init__(self, calculator=None, formatter=None, b2b_income=None):
        self.calculator = calculator
        self.formatter = formatter
        self.b2b_income = b2b_income
        self.data = calculator
        _ir_init(self, {'calculator': calculator, 'formatter': formatter, 'b2b_income': b2b_income})

    def show(self):
        """Shows the page in the Run Engine's Output tab, or updates it when it is already there."""
        return _ir_show(self)

    def zapisz(self):
        """Live action: the blocks wired to this output run again on every click. Zapisuje bieżące ustawienia i wyniki analizy jako nowy PDF w folderze output."""
        return _ir_wait(self, 'zapisz')

    def set(self, name, value, refresh=False):
        """Sets a state value; the markup sees it by name. refresh=True renders the page again."""
        self.state[name] = value
        if refresh:
            self.refresh()

    def get(self, name, default=None):
        """A state value — what a control bound to that name holds."""
        return self.state.get(name, default)

    def values(self):
        """A copy of the page's state."""
        return dict(self.state)

    def refresh(self):
        """Renders the page again and sends it to the Run Engine."""
        if self._ir['shown'] and not self._ir['closed']:
            _ir_push(self)

    def toast(self, message, kind='info'):
        """A short message over the page; kind is info, success, warning or error."""
        if self._ir['shown'] and not self._ir['closed'] and _ir_engine():
            _ir_send({'op': 'toast', 'id': self._ir['id'], 'message': str(message), 'kind': kind})
        else:
            print('[%s] %s' % (kind, message), flush=True)

    def close(self):
        """Closes the page; once every page is closed the run may end."""
        _ir_close(self)

    def bind_action(self, name, handler):
        """Calls handler(values) on every click of the action's button — what the generated main does with a live action."""
        _ir_bind(self, name, handler)

    # ── The Python tab ─────────────────────────────────────────────────────

    PARAMETER_NAMES = ("bank", "house_cost", "plot_value", "savings", "years", "build_months", "tranches", "rate_type",
                       "index_name", "index_rate_pct", "margin_pct", "fixed_rate_pct", "commission_pct",
                       "bridge_margin_pp", "bridge_months", "low_contribution_pp", "max_ltv_basic_pct",
                       "property_insurance_pct", "installment_type")
    COLORS = {"principal": "#3366cc", "interest": "#ff9900", "insurance": "#9aa5b1", "balance": "#109618",
              "living": "#7f8c9d", "obligations": "#c0392b", "rent": "#e67e22", "free": "#27ae60"}

    # ── Stan strony ──────────────────────────────────────────────────────────────

    def setup(self):
        self._apply_parameters(self.calculator.default_parameters())
        self._apply_budget(self.calculator.base_budget())

    def _apply_parameters(self, parameters):
        for name in self.PARAMETER_NAMES:
            value = getattr(parameters, name)
            self.set(name, round(value, 4) if isinstance(value, float) else value)

    def _apply_budget(self, budget):
        for index, (name, amount) in enumerate(budget.incomes):
            self.set("income_%d" % index, round(amount, 2))
            member = self._business_member(name)
            if member is not None:
                self.set("invoice_%d" % index, round(self._excel_invoice(member), 2))
        for index, item in enumerate(budget.expenses):
            self.set("expense_%d" % index, round(item.monthly, 2))

    def _budget_from(self, state):
        base = self.calculator.base_budget()
        incomes = {name: self._number(state.get("income_%d" % i), amount) for i, (name, amount) in enumerate(base.incomes)}
        expenses = {item.name: self._number(state.get("expense_%d" % i), item.monthly) for i, item in enumerate(base.expenses)}
        return base.with_amounts(incomes, expenses)

    @staticmethod
    def _number(value, default):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _analysis(self, state):
        parameters = MortgageParameters.from_state(state)
        result = {"parameters": parameters, "errors": parameters.validate(), "budget": self._budget_from(state)}
        if not result["errors"]:
            schedule = self.calculator.schedule(parameters)
            result["schedule"] = schedule
            result["assessment"] = self.calculator.assess(parameters, result["budget"], schedule)
            result["comparison"] = self.calculator.compare(parameters)
        return result

    # ── Reakcje na kontrolki ─────────────────────────────────────────────────────

    def on_bank_change(self, value):
        offer = self.calculator.offer(value)
        if offer:
            self._apply_parameters(self.calculator.parameters_for(offer, MortgageParameters.from_state(self.state)))

    def on_chosen_offer_change(self, row):
        if row and row.get("Bank"):
            self.set("bank", row["Bank"])
            self.on_bank_change(row["Bank"])

    def use_best_offer(self):
        parameters = MortgageParameters.from_state(self.state)
        if parameters.validate():
            self.toast("Najpierw popraw parametry.", "error")
            return
        best = self.calculator.compare(parameters)[0][0]
        self.set("bank", best.bank)
        self.on_bank_change(best.bank)
        self.toast("Wybrano najkorzystniejszą ofertę: %s." % best.bank, "success")

    def reset_offer(self):
        self.on_bank_change(self.get("bank"))
        self.toast("Przywrócono parametry oferty %s." % self.get("bank"), "info")

    def on_change(self, name, value):
        """Zmiana kwoty z faktury przelicza dochód na rękę tej osoby (ZUS, zdrowotna, PIT)."""
        match = re.match(r"invoice_(\d+)$", name)
        if not match:
            return
        index = int(match.group(1))
        member = self._business_member(self.calculator.base_budget().incomes[index][0])
        if member is not None:
            months = self._business_months(member, self._number(value, self._excel_invoice(member)))
            self.set("income_%d" % index, round(sum(m.net for m in months) / len(months), 2))

    def reset_budget(self):
        self._apply_budget(self.calculator.base_budget())
        self.toast("Przywrócono dochody i wydatki z pliku Excel.", "info")

    def reset_project(self):
        base = self.calculator.project_parameters()
        for name in ("house_cost", "plot_value", "savings", "years", "build_months", "tranches"):
            self.set(name, getattr(base, name))
        self.toast("Przywrócono plan budowy z pliku Excel.", "info")

    # ── Rysowanie ────────────────────────────────────────────────────────────────

    def prepare(self):
        a = self._analysis(self.state)
        p = a["parameters"]
        names = {
            "valid": not a["errors"],
            "status_line": self._status_line(),
            "bank_options": [(o.bank, "%s — %s + %s" % (o.bank, o.index_name, self.formatter.pct(o.margin_pct))) for o in self.calculator.offers],
            "index_options": list(self.calculator.rates.indices),
            "household_file": self.calculator.household.source,
            "business_rows": self._business_rows(self.state),
            "budget_controls": self._budget_controls(),
            "loan_amount": self.formatter.zl(p.amount),
            "own_contribution": "%s (%s wartości)" % (self.formatter.zl(p.own_contribution), self.formatter.pct(100 - p.ltv_pct, 1) if p.property_value else "—"),
            "message_box": self._messages(self._message_list(a)),
        }
        if a["errors"]:
            return names
        s, assessment = a["schedule"], a["assessment"]
        names.update({
            "kpis": html("".join(self._kpi(*item) for item in self._kpi_items(p, s, assessment))),
            "dsti": assessment.dsti_pct,
            "dsti_limit": assessment.dsti_limit_pct,
            "comparison_rows": self._comparison_rows(a["comparison"], p.bank),
            "comparison_chart": self._comparison_chart(a["comparison"], p.bank),
            "payment_chart": self._payment_chart(s),
            "budget_chart": self._budget_chart(a["budget"], s, assessment),
            "cost_rows": self._cost_rows(s),
            "assessment_rows": self._assessment_rows(p, assessment),
            "harmonogram": self._schedule_rows(s),
        })
        return names

    def _budget_controls(self):
        base = self.calculator.base_budget()
        parts = ['<h4>Dochody netto uznane przez bank [zł/mies.]</h4>']
        for index, (name, _) in enumerate(base.incomes):
            if self._business_member(name) is not None:
                parts.append(str(number("invoice_%d" % index, min=0, step=100,
                                        label=name + " — faktury netto, bez VAT [zł/mies.]")))
                parts.append(str(number("income_%d" % index, min=0, step=100,
                                        label="%s — na rękę po ZUS, zdrowotnej i PIT%s" % (name, self._business_note(index)))))
            else:
                parts.append(str(number("income_%d" % index, min=0, step=100, label=name)))
        parts.append('<h4>Wydatki [zł/mies.]</h4>')
        for index, item in enumerate(base.expenses):
            parts.append(str(number("expense_%d" % index, min=0, step=50, label="%s (%s)" % (item.name, item.kind))))
        if base.other_income:
            parts.append('<p class="cn-muted small">Dochód, którego bank nie wlicza (np. 800+): %s — liczony tylko w budżecie rodziny.</p>'
                         % esc(self.formatter.zl(base.other_income)))
        return html("".join(parts))

    def _status_line(self):
        r = self.calculator.rates
        offers_date = max((o.as_of for o in self.calculator.offers), default="")
        nbp = ("stopa referencyjna NBP %s od %s — pobrana z nbp.pl" % (self.formatter.pct(r.nbp_ref_now), r.nbp_date)
               if r.nbp_live else "brak połączenia z nbp.pl — stopa NBP z pliku (%s)" % self.formatter.pct(r.nbp_ref_now))
        indices = ", ".join("%s %s (%s)" % (name, self.formatter.pct(r.index_rate(name)), r.index_dates.get(name, ""))
                            for name in r.indices)
        shift = (" — przesunięte o %s pp po zmianie stopy NBP" % self.formatter.num(r.nbp_shift_pp, 2)
                 if abs(r.nbp_shift_pp) > 1e-9 else "")
        return "%s · wskaźniki: %s%s · oferty banków: stan na %s, plik input/oferty_bankow.xlsx" % (
            nbp, indices, shift, offers_date)

    def _message_list(self, a):
        if a["errors"]:
            return [(text, "error") for text in a["errors"]]
        assessment = a["assessment"]
        items = [(text, "error") for text in assessment.problems] + [(text, "warning") for text in assessment.warnings]
        if not assessment.problems:
            items.insert(0, ("Kredyt mieści się w zdolności kredytowej według reguł KNF przyjętych w modelu "
                             "(stopa z buforem %s, DSTI %s przy limicie %s)." % (
                                 self.formatter.pct(assessment.stress_rate_pct), self.formatter.pct(assessment.dsti_pct, 1),
                                 self.formatter.pct(assessment.dsti_limit_pct, 0)), "ok"))
        return items

    def _messages(self, items):
        if not items:
            return ""
        return html("".join('<div class="msg %s">%s</div>' % (kind, esc(text)) for text, kind in items))

    def _kpi_items(self, p, s, a):
        return [
            ("Kwota kredytu", self.formatter.zl(p.amount), "LTV %s · %d transze" % (self.formatter.pct(p.ltv_pct, 1), p.tranches), p.ltv_pct > a.max_ltv_pct),
            ("Rata po budowie", self.formatter.zl(s.first_full_payment), "w czasie budowy do %s" % self.formatter.zl(s.max_build_payment), False),
            ("RRSO", self.formatter.pct(s.rrso_pct), "oprocentowanie %s" % self.formatter.pct(p.nominal_rate_pct), False),
            ("Całkowity koszt", self.formatter.zl(s.total_cost), "do zapłaty razem %s" % self.formatter.zl(s.total_to_pay), False),
            ("Zdolność kredytowa", self.formatter.zl(a.max_amount), "maks. rata %s przy stresie" % self.formatter.zl(a.max_payment), p.amount > a.max_amount),
            ("DSTI przy stresie", self.formatter.pct(a.dsti_pct, 1), "limit %s · stopa %s" % (self.formatter.pct(a.dsti_limit_pct, 0), self.formatter.pct(a.stress_rate_pct)), a.dsti_pct > a.dsti_limit_pct),
            ("Wolne środki po przeprowadzce", self.formatter.zl(a.free_cash), "w czasie budowy %s" % self.formatter.zl(a.free_cash_build), a.free_cash < 0 or a.free_cash_build < 0),
            ("Wkład własny", self.formatter.zl(p.own_contribution), "działka %s + gotówka %s" % (self.formatter.zl(p.plot_value), self.formatter.zl(p.savings)), False),
        ]

    def _kpi(self, label, value, note, bad=False):
        return ('<div class="cn-kpi%s"><div class="cn-kpi-label">%s</div><div class="cn-kpi-value">%s</div>'
                '<div class="cn-kpi-delta cn-muted">%s</div></div>') % (" bad" if bad else "", esc(label), esc(value), esc(note))

    def _comparison_rows(self, comparison, chosen):
        rows = []
        for rank, (offer, s) in enumerate(comparison):
            rows.append({
                "": "★ najkorzystniejsza" if rank == 0 else ("● wybrana" if offer.bank == chosen else ""),
                "Bank": offer.bank, "Wskaźnik": offer.index_name, "Marża [%]": offer.margin_pct,
                "Prowizja [%]": offer.commission_pct, "Oproc. [%]": round(s.parameters.nominal_rate_pct, 2),
                "Rata po budowie [zł]": round(s.first_full_payment), "Koszt całkowity [zł]": round(s.total_cost),
                "RRSO [%]": round(s.rrso_pct, 2), "Uwagi": offer.notes,
            })
        return rows

    def _comparison_chart(self, comparison, chosen):
        banks = [offer.bank for offer, _ in comparison][::-1]
        costs = [round(s.total_cost) for _, s in comparison][::-1]
        colors = ["#1f4e8c" if bank == chosen else "#9aa5b1" for bank in banks]
        return {"data": [{"type": "bar", "orientation": "h", "x": costs, "y": banks, "marker": {"color": colors},
                          "text": [self.formatter.zl(c) for c in costs], "textposition": "auto", "hoverinfo": "y+text"}],
                "layout": {"height": 300, "title": {"text": "Całkowity koszt kredytu w bankach"},
                           "margin": {"l": 160, "r": 20, "t": 50, "b": 40}, "xaxis": {"title": {"text": "zł"}},
                           "paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)"}}

    def _payment_chart(self, s):
        years = s.yearly()
        x = [y[0] for y in years]
        bar = lambda name, values, color: {"type": "bar", "name": name, "x": x, "y": [round(v) for v in values], "marker": {"color": color}}
        return {"data": [
                    bar("Kapitał", [y[1] for y in years], self.COLORS["principal"]),
                    bar("Odsetki", [y[2] for y in years], self.COLORS["interest"]),
                    bar("Ubezpieczenie", [y[3] for y in years], self.COLORS["insurance"]),
                    {"type": "scatter", "mode": "lines", "name": "Saldo na koniec roku", "x": x, "y": [round(y[4]) for y in years],
                     "yaxis": "y2", "line": {"color": self.COLORS["balance"], "width": 2}}],
                "layout": {"barmode": "stack", "height": 380, "title": {"text": "Spłaty w kolejnych latach i saldo zadłużenia"},
                           "margin": {"l": 70, "r": 70, "t": 50, "b": 40}, "legend": {"orientation": "h", "y": -0.18},
                           "xaxis": {"title": {"text": "rok kredytu"}}, "yaxis": {"title": {"text": "spłaty w roku [zł]"}},
                           "yaxis2": {"title": {"text": "saldo [zł]"}, "overlaying": "y", "side": "right", "showgrid": False},
                           "paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)"}}

    def _budget_chart(self, budget, s, a):
        phases = ["W czasie budowy", "Po przeprowadzce"]
        part = lambda name, values, color: {"type": "bar", "name": name, "x": phases, "y": [round(v) for v in values], "marker": {"color": color}}
        return {"data": [
                    part("Koszty życia", [a.living_costs, a.living_costs], self.COLORS["living"]),
                    part("Inne zobowiązania", [a.obligations, a.obligations], self.COLORS["obligations"]),
                    part("Najem do końca budowy", [budget.other_costs, 0], self.COLORS["rent"]),
                    part("Rata kredytu", [s.max_build_payment, s.first_full_payment], self.COLORS["principal"]),
                    part("Wolne środki", [max(a.free_cash_build, 0), max(a.free_cash, 0)], self.COLORS["free"])],
                "layout": {"barmode": "stack", "height": 380, "title": {"text": "Miesięczny budżet rodziny"},
                           "margin": {"l": 70, "r": 20, "t": 50, "b": 40}, "legend": {"orientation": "h", "y": -0.12},
                           "yaxis": {"title": {"text": "zł / mies."}},
                           "paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)"}}

    def _cost_rows(self, s):
        rows = [{"Składnik": "Odsetki", "zł": round(s.total_interest)},
                {"Składnik": "Ubezpieczenie nieruchomości", "zł": round(s.total_insurance)},
                {"Składnik": "Prowizja", "zł": round(s.parameters.commission)}]
        return [row for row in rows if row["zł"] > 0]

    def _assessment_rows(self, p, a):
        rows = [
            ("Dochód netto uznany przez bank", self.formatter.zl(a.income)),
            ("Koszty życia (zadeklarowane lub minimum banku)", self.formatter.zl(a.living_costs)),
            ("Inne zobowiązania (raty, limity kart)", self.formatter.zl(a.obligations)),
            ("Oprocentowanie do testu (z buforem KNF)", self.formatter.pct(a.stress_rate_pct)),
            ("Rata przy teście", self.formatter.zl(a.stress_payment)),
            ("DSTI przy teście / limit", "%s / %s" % (self.formatter.pct(a.dsti_pct, 1), self.formatter.pct(a.dsti_limit_pct, 0))),
            ("Maksymalna rata", self.formatter.zl(a.max_payment)),
            ("Zdolność kredytowa (maks. kwota)", self.formatter.zl(a.max_amount)),
            ("LTV / maks. LTV banku", "%s / %s" % (self.formatter.pct(a.ltv_pct, 1), self.formatter.pct(a.max_ltv_pct, 0))),
        ]
        return [{"Pozycja": name, "Wartość": value} for name, value in rows]

    def _schedule_rows(self, s):
        return [{"Nr": i.number, "Faza": i.phase, "Transza": round(i.disbursed, 2), "Kapitał": round(i.principal, 2),
                 "Odsetki": round(i.interest, 2), "Ubezpieczenie": round(i.insurance, 2), "Rata łącznie": round(i.total, 2),
                 "Oproc. [%]": round(i.rate_pct, 2), "Saldo": round(i.balance_after, 2)} for i in s.installments]

    # ── Zapis do PDF ─────────────────────────────────────────────────────────────

    def on_zapisz(self, values):
        a = self._analysis(values)
        if a["errors"]:
            self.toast("Popraw parametry — analiza z błędami nie zostanie zapisana.", "error")
            return None
        self.toast("Zapisuję analizę do PDF w folderze output…", "info")
        p, s, assessment, budget = a["parameters"], a["schedule"], a["assessment"], a["budget"]
        return MortgageReportSnapshot(
            title="Kredyt hipoteczny na budowę domu — analiza",
            created_at=datetime.now(),
            kpis=tuple(self._kpi_items(p, s, assessment)),
            messages=tuple(self._message_list(a)),
            tables=(
                self._table("Parametry kredytu", ("Parametr", "Wartość"), self._parameter_rows(p), widths=(0.45, 0.55)),
                self._table("Ocena zdolności kredytowej", ("Pozycja", "Wartość"),
                            [(r["Pozycja"], r["Wartość"]) for r in self._assessment_rows(p, assessment)], right=(1,), widths=(0.7, 0.3)),
                *([self._table("Dochód z działalności (B2B) — średnio miesięcznie",
                               ("Osoba", "Rozliczenie", "Faktury", "Koszty", "ZUS społ.", "Zdrowotna", "PIT", "Na rękę"),
                               [tuple(row.values()) for row in self._business_rows(values, formatted=True)],
                               right=(2, 3, 4, 5, 6, 7), widths=(1.3, 1.6, 0.9, 0.7, 0.8, 0.8, 0.7, 0.9))]
                  if self._business_rows(values) else []),
                self._table("Budżet rodziny (miesięcznie)", ("Pozycja", "Rodzaj", "Kwota"), self._budget_rows(budget), right=(2,), widths=(0.55, 0.25, 0.2)),
                self._table("Porównanie banków (ten sam plan budowy)",
                            ("Bank", "Wskaźnik", "Marża", "Oproc.", "Rata po budowie", "Koszt całkowity", "RRSO"),
                            [(o.bank, o.index_name, self.formatter.pct(o.margin_pct), self.formatter.pct(c.parameters.nominal_rate_pct),
                              self.formatter.zl(c.first_full_payment), self.formatter.zl(c.total_cost), self.formatter.pct(c.rrso_pct))
                             for o, c in a["comparison"]], right=(2, 3, 4, 5, 6), widths=(1.6, 0.9, 0.7, 0.7, 1.1, 1.2, 0.7)),
                self._table("Harmonogram spłat", ("Nr", "Faza", "Transza", "Kapitał", "Odsetki", "Ubezp.", "Rata", "Saldo"),
                            [(str(i.number), i.phase, self.formatter.num(i.disbursed, 2) if i.disbursed else "", self.formatter.num(i.principal, 2),
                              self.formatter.num(i.interest, 2), self.formatter.num(i.insurance, 2), self.formatter.num(i.total, 2),
                              self.formatter.num(i.balance_after, 2)) for i in s.installments],
                            right=(0, 2, 3, 4, 5, 6, 7), widths=(0.45, 0.7, 1, 1, 1, 0.8, 1, 1.2)),
            ),
            schedule=s,
            notes=(self._status_line(),
                   "Ocena zdolności według uproszczonych reguł Rekomendacji S KNF; oferty banków orientacyjne — "
                   "decyzję i warunki podaje bank."),
        )

    @staticmethod
    def _table(title, header, rows, right=(), widths=()):
        return ReportTable(title=title, header=tuple(header), rows=tuple(tuple(str(c) for c in row) for row in rows),
                           right_columns=tuple(right), widths=tuple(widths))

    def _parameter_rows(self, p):
        rate = ("zmienne: %s %s + marża %s" % (p.index_name, self.formatter.pct(p.index_rate_pct), self.formatter.pct(p.margin_pct))
                if p.rate_type == MortgageParameters.VARIABLE else "okresowo stałe")
        return [
            ("Bank", p.bank or "—"),
            ("Koszt budowy domu", self.formatter.zl(p.house_cost)),
            ("Wartość działki (wkład własny)", self.formatter.zl(p.plot_value)),
            ("Oszczędności wkładane w budowę", self.formatter.zl(p.savings)),
            ("Kwota kredytu / LTV", "%s / %s" % (self.formatter.zl(p.amount), self.formatter.pct(p.ltv_pct, 1))),
            ("Okres kredytu", "%d lat (%d rat)" % (p.years, p.months)),
            ("Budowa", "%d mies., %d transz(e)" % (p.build_months, p.tranches)),
            ("Oprocentowanie", "%s → %s rocznie" % (rate, self.formatter.pct(p.nominal_rate_pct))),
            ("Podwyższenie do wpisu hipoteki", "+%s pp przez %d mies." % (self.formatter.num(p.bridge_margin_pp, 2), p.bridge_months)),
            ("Prowizja", "%s = %s" % (self.formatter.pct(p.commission_pct), self.formatter.zl(p.commission))),
            ("Ubezpieczenie nieruchomości", "%s wartości rocznie" % self.formatter.pct(p.property_insurance_pct)),
            ("Rodzaj rat", p.installment_type),
        ]

    def _business_member(self, name):
        return next((m for m in self.calculator.household.members if m.name == name and m.business), None)

    @staticmethod
    def _excel_invoice(member):
        return sum(m.invoiced for m in member.business) / len(member.business)

    def _business_months(self, member, invoice):
        """Miesiące z Excela, dopóki kwota z faktury jest ta sama; po zmianie — 12 miesięcy po tej kwocie."""
        if abs(invoice - self._excel_invoice(member)) < 0.5:
            return list(member.business)
        return self.b2b_income.months([invoice] * 12, member.tax_profile)

    def _business_rows(self, state, formatted=False):
        """Dla domowników rozliczających działalność z faktur: średnio miesięcznie faktury → ZUS, zdrowotna, PIT → na rękę."""
        rows = []
        for index, (name, _) in enumerate(self.calculator.base_budget().incomes):
            member = self._business_member(name)
            if member is None:
                continue
            months = self._business_months(member, self._number(state.get("invoice_%d" % index), self._excel_invoice(member)))
            average = lambda pick: sum(pick(m) for m in months) / len(months)
            values = [average(lambda m: m.invoiced), average(lambda m: m.costs), average(lambda m: m.social),
                      average(lambda m: m.health), average(lambda m: m.tax), average(lambda m: m.net)]
            values = [self.formatter.zl(v) for v in values] if formatted else [round(v) for v in values]
            rows.append(dict(zip(("Osoba", "Rozliczenie", "Faktury [zł]", "Koszty [zł]", "ZUS społeczny [zł]",
                                  "Zdrowotna [zł]", "PIT [zł]", "Na rękę [zł]"),
                                 [member.name, member.tax_profile.label] + values)))
        return rows

    def _business_note(self, index):
        rows = self._business_rows(self.state)
        row = next((r for r in rows if r["Osoba"] == self.calculator.base_budget().incomes[index][0]), None)
        return " (z faktur wychodzi %s)" % self.formatter.zl(row["Na rękę [zł]"]) if row else ""

    def _budget_rows(self, budget):
        rows = [(name, "dochód uznany przez bank", self.formatter.zl(amount)) for name, amount in budget.incomes]
        if budget.other_income:
            rows.append(("Dochód niewliczany przez bank", "dochód", self.formatter.zl(budget.other_income)))
        rows += [(item.name, item.kind, self.formatter.zl(item.monthly)) for item in budget.expenses]
        return rows


# ── CatNip interactive report runtime ─────────────────────────────────────────
# Generated with the class above; everything here is shared by every interactive report of a
# process through one hub, so two reports on one page of output never fight over stdin.
#
# The page lives in CatNip's Run Engine. It reaches this process as lines on stdin
# (__CATNIP_UI__ {json}) and this process answers through the ordinary visual stream
# (__VISUAL_START__ {"type": "interactive", ...} __VISUAL_END__) — the two channels every kind of
# run already has, locally, in Docker, in a compiled executable and on the CatNip Server.

_IR_PREFIX = '__CATNIP_UI__'
_IR_LOCAL = _ir_threading.local()


class Html(str):
    """Text that goes into the page as HTML instead of being escaped."""
    __slots__ = ()

    def __html__(self):
        return str(self)


def html(text):
    """Marks text as HTML, to be inserted as it is."""
    return Html('' if text is None else text)


def esc(value):
    """Escapes a value for the page."""
    return _ir_html.escape('' if value is None else str(value), quote=True)


def fmt(value, spec=None):
    """Formats a value with a format spec (',.2f', '.1%', ...); None reads as empty."""
    if value is None:
        return ''
    if not spec:
        return str(value)
    try:
        return format(value, spec)
    except (TypeError, ValueError):
        return str(value)


# ── The hub: one per process ──────────────────────────────────────────────────

def _ir_hub():
    hub = getattr(_ir_sys, '_catnip_interactive_hub', None)
    if hub is None:
        hub = {
            'pages': {},
            'lock': _ir_threading.RLock(),
            'out': _ir_threading.Lock(),
            'reader': None,
            'keeper': None,
            'closed': _ir_threading.Event(),
            'eof': False,
        }
        setattr(_ir_sys, '_catnip_interactive_hub', hub)
    return hub


def _ir_engine():
    """True when a CatNip engine is listening on the other end of stdout and stdin."""
    env = _ir_os.environ
    return bool(env.get('CATNIP_MAIN_PY') or env.get('CATNIP_SCRIPT')
                or env.get('CATNIP_ENGINE') or env.get('CATNIP_INTERACTIVE'))


def _ir_plain(value):
    """A value JSON can carry: numpy scalars, dates, decimals and the like are reduced to one."""
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value if _ir_math.isfinite(value) else None
    if isinstance(value, (list, tuple)):
        return [_ir_plain(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _ir_plain(v) for k, v in value.items()}
    if hasattr(value, 'item') and not hasattr(value, '__len__'):
        try:
            return _ir_plain(value.item())
        except Exception:
            pass
    if hasattr(value, 'tolist'):
        try:
            return _ir_plain(value.tolist())
        except Exception:
            pass
    if hasattr(value, 'isoformat'):
        try:
            return value.isoformat()
        except Exception:
            pass
    try:
        import decimal
        if isinstance(value, decimal.Decimal):
            return float(value)
    except Exception:
        pass
    return str(value)


def _ir_json(value):
    return _ir_json_module.dumps(_ir_plain(value), separators=(',', ':'), ensure_ascii=False)


def _ir_send(message):
    body = _ir_json(message).encode('utf-8')
    payload = _ir_json_module.dumps({
        'type': 'interactive',
        'title': message.get('title', ''),
        'data': _ir_base64.b64encode(body).decode('ascii'),
    })
    with _ir_hub()['out']:
        _ir_sys.stdout.write('__VISUAL_START__' + payload + '__VISUAL_END__\n')
        _ir_sys.stdout.flush()


def _ir_register(page, keep_alive):
    hub = _ir_hub()
    with hub['lock']:
        hub['pages'][page._ir['id']] = page
        if hub['eof']:
            return
        if hub['reader'] is None:
            hub['reader'] = _ir_threading.Thread(target=_ir_read_loop, name='catnip-interactive', daemon=True)
            hub['reader'].start()
        # The keeper is what keeps the process alive after the flow finished: the reader is a
        # daemon thread and would die with the main one.
        if keep_alive and hub['keeper'] is None:
            hub['keeper'] = _ir_threading.Thread(target=hub['closed'].wait, name='catnip-interactive-keeper')
            hub['keeper'].start()


def _ir_unregister(page_id):
    hub = _ir_hub()
    with hub['lock']:
        hub['pages'].pop(page_id, None)
        if not hub['pages']:
            hub['closed'].set()


def _ir_read_loop():
    hub = _ir_hub()
    stream = _ir_sys.stdin
    while True:
        try:
            line = stream.readline() if stream is not None else ''
        except Exception:
            line = ''
        if not line:
            # Nobody will ever answer again (the run was stopped, or nothing was attached):
            # whoever is waiting for a click must be let go, and the process may end.
            with hub['lock']:
                hub['eof'] = True
                pages = list(hub['pages'].values())
            for page in pages:
                _ir_release_waiters(page)
            hub['closed'].set()
            return
        line = line.strip()
        if not line.startswith(_IR_PREFIX):
            continue
        try:
            message = _ir_json_module.loads(line[len(_IR_PREFIX):])
        except ValueError:
            continue
        with hub['lock']:
            page = hub['pages'].get(message.get('page'))
        if page is None:
            continue
        try:
            _ir_dispatch(page, message)
        except Exception:
            _ir_traceback.print_exc()


# ── A page ────────────────────────────────────────────────────────────────────

def _ir_init(page, inputs):
    page.state = {}
    page._ir = {
        'id': _ir_uuid.uuid4().hex,
        'shown': False,
        'closed': False,
        'bindings': {},
        'waiters': {},
        'pending': {},
        'controls': {},
        'counter': 0,
        'inputs': inputs,
        'lock': _ir_threading.RLock(),
    }
    setup = getattr(page, 'setup', None)
    if callable(setup):
        setup()


def _ir_show(page):
    ir = page._ir
    if ir['closed']:
        return None
    if not _ir_engine():
        print('[CatNip] %s: an interactive report is shown by the CatNip Run Engine; '
              'outside it there is no page to show.' % type(page).TITLE, flush=True)
        return None
    if _ir_sys.gettrace() is not None:
        # A debugger reads stdin too, and the page would steal its commands.
        print('[CatNip] %s: the page stays static while debugging.' % type(page).TITLE, flush=True)
        ir['shown'] = True
        _ir_push(page, interactive=False)
        return None
    ir['shown'] = True
    _ir_register(page, type(page).KEEP_ALIVE)
    _ir_push(page)
    return None


def _ir_push(page, interactive=True):
    """Renders the page and sends it; the Run Engine replaces the card with the same id."""
    cls = type(page)
    try:
        body = _ir_render(page)
    except Exception as ex:
        _ir_traceback.print_exc()
        body = '<div class="cn-error-page"><b>The page could not be rendered.</b><pre>%s</pre></div>' % esc(
            '%s: %s' % (type(ex).__name__, ex))
    _ir_send({
        'op': 'render',
        'id': page._ir['id'],
        'title': cls.TITLE,
        'height': cls.HEIGHT,
        'css': cls.STYLE,
        'html': body,
        'interactive': interactive,
        'actions': dict(cls.ACTIONS),
    })


def _ir_namespace(page):
    namespace = dict(globals())
    prepare = getattr(page, 'prepare', None)
    extra = prepare() if callable(prepare) else None
    namespace.update(page.state)
    for name, value in page._ir['inputs'].items():
        namespace[name] = getattr(page, name, value)
    namespace.update({'self': page, 'state': page.state, 'data': page.data, 'title': type(page).TITLE})
    if isinstance(extra, dict):
        namespace.update(extra)
    return namespace


def _ir_render(page):
    with page._ir['lock']:
        page._ir['counter'] = 0
        page._ir['controls'] = {}
        previous = (getattr(_IR_LOCAL, 'page', None), getattr(_IR_LOCAL, 'namespace', None))
        _IR_LOCAL.page = page
        _IR_LOCAL.namespace = None
        try:
            namespace = _ir_namespace(page)
            # A control placed further up gives its state value a default as it renders; the holes
            # below it must see that value, so the namespace is shared with _ir_default.
            _IR_LOCAL.namespace = namespace
            return _ir_template(type(page).MARKUP, namespace)
        finally:
            _IR_LOCAL.page, _IR_LOCAL.namespace = previous


def _ir_current():
    page = getattr(_IR_LOCAL, 'page', None)
    if page is None:
        raise RuntimeError('controls, charts and tables are placed from the markup, while the page renders')
    return page


def _ir_next_id(prefix):
    page = getattr(_IR_LOCAL, 'page', None)
    if page is None:
        return 'cn-%s-%s' % (prefix, _ir_uuid.uuid4().hex[:8])
    page._ir['counter'] += 1
    return 'cn-%s-%d' % (prefix, page._ir['counter'])


def _ir_dispatch(page, message):
    op = message.get('op')
    if op == 'ready':
        _ir_push(page)
        return
    if op == 'close':
        _ir_close(page, notify=False)
        return
    if op == 'change':
        name = str(message.get('name') or '')
        if not name:
            return
        value = message.get('value')
        page.state[name] = value
        hook = getattr(page, 'on_%s_change' % name, None)
        if callable(hook):
            _ir_guard(page, hook, value)
        else:
            hook = getattr(page, 'on_change', None)
            if callable(hook):
                _ir_guard(page, hook, name, value)
        _ir_push(page)
        return
    if op == 'call':
        name = str(message.get('name') or '')
        method = getattr(page, name, None) if name and not name.startswith('_') else None
        if callable(method):
            _ir_guard(page, method)
        else:
            page.toast('The page has no method called %s.' % name, 'error')
        _ir_push(page)
        return
    if op == 'action':
        _ir_fire(page, str(message.get('name') or ''))


def _ir_guard(page, func, *args):
    try:
        return func(*args)
    except Exception as ex:
        _ir_traceback.print_exc()
        page.toast('%s: %s' % (type(ex).__name__, ex), 'error')
        return None


def _ir_payload(page, name):
    values = dict(page.state)
    hook = getattr(page, 'on_' + name, None)
    if callable(hook):
        result = hook(values)
        if result is not None:
            return result
    return values


def _ir_fire(page, name):
    ir = page._ir
    if name not in type(page).ACTIONS:
        page.toast('The page has no action called %s.' % name, 'error')
        return
    with ir['lock']:
        waiter = ir['waiters'].pop(name, None)
        binding = ir['bindings'].get(name)
    try:
        payload = _ir_payload(page, name)
    except Exception as ex:
        _ir_traceback.print_exc()
        page.toast('%s: %s' % (type(ex).__name__, ex), 'error')
        return
    if waiter is not None:
        waiter['payload'] = payload
        waiter['event'].set()
        return
    if (binding is None and type(page).ACTIONS.get(name) == 'live'
            and _ir_threading.main_thread().is_alive()
            and _ir_os.environ.get('CATNIP_INTERACTIVE') != 'preview'):
        # The generated main binds live actions after the rest of the flow has been called, and
        # the flow may still be on its way there (waiting at a submit, say): the click is kept
        # and handled the moment the binding arrives.
        with ir['lock']:
            ir['pending'][name] = payload
        page.toast('"%s" runs as soon as the flow reaches it.' % name, 'info')
        return
    if binding is None:
        if _ir_os.environ.get('CATNIP_INTERACTIVE') == 'preview':
            page.toast('%s would hand over: %s' % (name, _ir_json(payload)[:400]), 'info')
        else:
            page.toast('Nothing is waiting for "%s" — connect a block to its output and run the generated main.' % name, 'warning')
        return
    _ir_run_binding(page, name, binding, payload)


def _ir_run_binding(page, name, binding, payload):
    ir = page._ir
    _ir_send({'op': 'busy', 'id': ir['id'], 'on': True, 'label': name})
    try:
        _ir_guard(page, binding, payload)
    finally:
        _ir_send({'op': 'busy', 'id': ir['id'], 'on': False})
        _ir_push(page)


def _ir_bind(page, name, handler):
    ir = page._ir
    with ir['lock']:
        ir['bindings'][name] = handler
        pending = ir['pending'].pop(name, None)
    if pending is not None:
        _ir_run_binding(page, name, handler, pending)


def _ir_wait(page, name):
    """The output of a submit action: shows the page if it is not shown, then waits for the click."""
    ir = page._ir
    if not ir['shown']:
        page.show()
    hub = _ir_hub()
    if ir['closed'] or not _ir_engine() or hub['eof'] or _ir_sys.gettrace() is not None:
        # Nobody can click: carry on with what the page holds.
        return _ir_payload(page, name)
    waiter = {'event': _ir_threading.Event(), 'payload': None}
    with ir['lock']:
        ir['waiters'][name] = waiter
    _ir_send({'op': 'waiting', 'id': ir['id'], 'action': name})
    waiter['event'].wait()
    _ir_send({'op': 'waiting', 'id': ir['id'], 'action': None})
    return waiter['payload']


def _ir_release_waiters(page):
    with page._ir['lock']:
        waiters = list(page._ir['waiters'].values())
        page._ir['waiters'].clear()
    for waiter in waiters:
        waiter['event'].set()


def _ir_close(page, notify=True):
    ir = page._ir
    if ir['closed']:
        return
    ir['closed'] = True
    _ir_release_waiters(page)
    if notify and ir['shown']:
        _ir_send({'op': 'close', 'id': ir['id']})
    _ir_unregister(ir['id'])


# ── The template: HTML with {python} holes ───────────────────────────────────

_IR_COMPILED = {}


def _ir_template(text, namespace):
    out = []
    i = 0
    n = len(text)
    lower = text.lower()
    while i < n:
        c = text[i]
        if c == '<' and (lower.startswith('<script', i) or lower.startswith('<style', i)):
            # Script and style blocks are copied as they are: their braces are not holes.
            tag = 'script' if lower.startswith('<script', i) else 'style'
            end = lower.find('</' + tag, i)
            end = n if end < 0 else lower.find('>', end) + 1 or n
            out.append(text[i:end])
            i = end
            continue
        if c == '{':
            if text.startswith('{{', i):
                out.append('{')
                i += 2
                continue
            close = _ir_matching(text, i)
            if close < 0:
                out.append(text[i:])
                break
            out.append(_ir_hole(text[i + 1:close], namespace))
            i = close + 1
            continue
        if c == '}':
            out.append('}')
            i += 2 if text.startswith('}}', i) else 1
            continue
        nxt = min([p for p in (text.find('{', i), text.find('}', i), lower.find('<s', i)) if p >= 0] or [n])
        if nxt == i:
            nxt = i + 1
        out.append(text[i:nxt])
        i = nxt
    return ''.join(out)


def _ir_matching(text, start):
    """The brace closing the one at start, skipping braces inside strings and nested brackets."""
    depth = 0
    quote = None
    i = start
    while i < len(text):
        c = text[i]
        if quote:
            if c == '\\':
                i += 2
                continue
            if text.startswith(quote, i):
                i += len(quote)
                quote = None
                continue
        elif c in '\'"':
            quote = c * 3 if text.startswith(c * 3, i) else c
            i += len(quote)
            continue
        elif c in '{[(':
            depth += 1
        elif c in '}])':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _ir_hole(expression, namespace):
    raw = expression.startswith('!')
    source = expression[1:] if raw else expression
    source = source.strip()
    if not source:
        return ''
    try:
        code = _IR_COMPILED.get(source)
        if code is None:
            code = compile(source, '<markup {%s}>' % source[:60], 'eval')
            _IR_COMPILED[source] = code
        value = eval(code, namespace)
    except Exception as ex:
        return '<span class="cn-error" title="%s">{%s} → %s: %s</span>' % (
            esc(source), esc(source[:80]), esc(type(ex).__name__), esc(ex))
    return _ir_value(value, raw)


def _ir_value(value, raw=False):
    if value is None:
        return ''
    if hasattr(value, '__html__'):
        return str(value.__html__())
    if raw:
        return str(value)
    if hasattr(value, 'to_plotly_json'):
        return plotly(value)
    if hasattr(value, 'savefig'):
        return figure(value)
    if hasattr(value, 'columns') and hasattr(value, 'itertuples'):
        return table(value)
    if isinstance(value, float):
        return esc(_ir_number(value))
    return esc(value)


def _ir_number(value):
    if value != value:
        return ''
    if float(value).is_integer() and abs(value) < 1e15:
        return str(int(value))
    return ('%.6g' % value) if abs(value) < 1e-4 or abs(value) >= 1e15 else str(round(value, 6))


# ── Data shapes ───────────────────────────────────────────────────────────────

def _ir_table(rows, columns=None, limit=0):
    """(headers, rows of values) out of a DataFrame, numpy array, dict of columns, list of dicts
    or list of rows — resolved when the page renders, so the data may change shape between runs."""
    if rows is None:
        return [], []
    limit = int(limit or 0)
    if hasattr(rows, 'columns') and hasattr(rows, 'itertuples'):
        frame = rows[list(columns)] if columns else rows
        if limit > 0:
            frame = frame.head(limit)
        return [str(c) for c in frame.columns], [list(r) for r in frame.itertuples(index=False, name=None)]
    if hasattr(rows, 'column_names') and hasattr(rows, 'to_pylist'):          # pyarrow Table
        return _ir_table(rows.to_pylist(), columns, limit)
    if hasattr(rows, 'tolist') and not isinstance(rows, (list, tuple, dict)):
        rows = rows.tolist()
    if isinstance(rows, dict):
        headers = [str(k) for k in (columns or rows.keys())]
        cols = [rows.get(h, []) for h in headers]
        cols = [c.tolist() if hasattr(c, 'tolist') else list(c) if hasattr(c, '__iter__') and not isinstance(c, str) else [c] for c in cols]
        length = max((len(c) for c in cols), default=0)
        if limit > 0:
            length = min(length, limit)
        return headers, [[c[i] if i < len(c) else None for c in cols] for i in range(length)]
    rows = list(rows)
    if not rows:
        return [str(c) for c in (columns or [])], []
    if limit > 0:
        rows = rows[:limit]
    if isinstance(rows[0], dict):
        headers = [str(k) for k in (columns or rows[0].keys())]
        return headers, [[row.get(h) for h in headers] for row in rows]
    if hasattr(rows[0], '_fields'):                                            # namedtuple
        headers = list(columns or rows[0]._fields)
        return headers, [[getattr(row, h, None) for h in headers] for row in rows]
    cells = [list(row) if hasattr(row, '__iter__') and not isinstance(row, str) else [row] for row in rows]
    width = max(len(r) for r in cells)
    headers = [str(c) for c in columns] if columns else ['Column %d' % (i + 1) for i in range(width)]
    return headers, cells


def rows_of(data, columns=None):
    """Any tabular shape as a list of dicts — the easiest form to compute with in a report."""
    if data is None:
        return []
    headers, cells = _ir_table(data, columns)
    return [dict(zip(headers, row)) for row in cells]


def column(data, key):
    """One column of any tabular shape as a list; a sequence passed as the key comes back as a list."""
    if key is None:
        return None
    if not isinstance(key, str):
        return key.tolist() if hasattr(key, 'tolist') else list(key)
    if data is None:
        raise KeyError('no data to take the column %r from' % key)
    if hasattr(data, 'columns') and hasattr(data, 'itertuples'):
        return data[key].tolist()
    if isinstance(data, dict):
        values = data[key]
        return values.tolist() if hasattr(values, 'tolist') else list(values)
    headers, cells = _ir_table(data)
    if key not in headers:
        raise KeyError('no column %r — the data has %s' % (key, ', '.join(headers) or 'no columns'))
    index = headers.index(key)
    return [row[index] if index < len(row) else None for row in cells]


def _ir_data(data):
    if data is None:
        page = getattr(_IR_LOCAL, 'page', None)
        return page.data if page is not None else None
    return data


def _ir_attrs(**attributes):
    parts = []
    for key, value in attributes.items():
        if value is None or value is False:
            continue
        key = key.rstrip('_').replace('_', '-')
        parts.append(key if value is True else '%s="%s"' % (key, esc(value)))
    return ' '.join(parts)


def _ir_json_block(value):
    return _ir_json(value).replace('</', '<\\/')


def _ir_label(label, for_id, body, css='cn-field'):
    caption = '<label class="cn-label" for="%s">%s</label>' % (for_id, esc(label)) if label else ''
    return Html('<div class="%s">%s%s</div>' % (css, caption, body))


def _ir_default(name, value):
    page = _ir_current()
    if name not in page.state:
        page.state[name] = value
        namespace = getattr(_IR_LOCAL, 'namespace', None)
        if namespace is not None:
            namespace.setdefault(name, value)
    page._ir['controls'][name] = True
    return page.state[name]


# ── Controls: each one is bound to the state value of its name ───────────────

def slider(name, min=0, max=100, step=1, value=None, label=None, live=False, format=None):
    """A slider; the state value changes when it is released, or while dragging with live=True."""
    current = _ir_default(name, min if value is None else value)
    control_id = 'cn-' + name
    shown = fmt(current, format)
    body = ('<div class="cn-slider-row"><input type="range" %s/><output class="cn-slider-value" data-cn-format="%s">%s</output></div>'
            % (_ir_attrs(id=control_id, class_='cn-slider', min=min, max=max, step=step, value=current,
                         data_cn_bind=name, data_cn_type='number', data_cn_live='1' if live else None),
               esc(format or ''), esc(shown)))
    return _ir_label(label, control_id, body)


def number(name, value=None, min=None, max=None, step=None, label=None, integer=False):
    """A number box."""
    current = _ir_default(name, 0 if value is None else value)
    control_id = 'cn-' + name
    body = '<input type="number" %s/>' % _ir_attrs(
        id=control_id, class_='cn-input', value=current, min=min, max=max, step=step if step is not None else (1 if integer else 'any'),
        data_cn_bind=name, data_cn_type='int' if integer else 'number')
    return _ir_label(label, control_id, body)


def text_input(name, value='', label=None, placeholder=None):
    """A one-line text box; the state value changes when it loses focus or Enter is pressed."""
    current = _ir_default(name, value)
    control_id = 'cn-' + name
    body = '<input type="text" %s/>' % _ir_attrs(
        id=control_id, class_='cn-input', value=current, placeholder=placeholder, data_cn_bind=name, data_cn_type='text')
    return _ir_label(label, control_id, body)


def textarea(name, value='', label=None, rows=4, placeholder=None):
    """A multi-line text box."""
    current = _ir_default(name, value)
    control_id = 'cn-' + name
    body = '<textarea %s>%s</textarea>' % (_ir_attrs(
        id=control_id, class_='cn-input', rows=rows, placeholder=placeholder, data_cn_bind=name, data_cn_type='text'), esc(current))
    return _ir_label(label, control_id, body)


def _ir_options(options):
    if options is None:
        return []
    if isinstance(options, dict):
        return [(k, v) for k, v in options.items()]
    if hasattr(options, 'tolist'):
        options = options.tolist()
    result = []
    for option in options:
        if isinstance(option, (list, tuple)) and len(option) == 2:
            result.append((option[0], option[1]))
        else:
            result.append((option, option))
    return result


def _ir_option_type(pairs):
    values = [v for v, _ in pairs]
    if values and all(isinstance(v, bool) for v in values):
        return 'bool'
    if values and all(isinstance(v, int) and not isinstance(v, bool) for v in values):
        return 'int'
    if values and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
        return 'number'
    return 'text'


def select(name, options, value=None, label=None):
    """A combo box. Options are values, (value, caption) pairs or a {value: caption} dictionary."""
    pairs = _ir_options(options)
    current = _ir_default(name, value if value is not None else (pairs[0][0] if pairs else None))
    control_id = 'cn-' + name
    items = ''.join('<option value="%s"%s>%s</option>' % (esc(v), ' selected' if v == current else '', esc(c)) for v, c in pairs)
    body = '<select %s>%s</select>' % (_ir_attrs(
        id=control_id, class_='cn-input', data_cn_bind=name, data_cn_type=_ir_option_type(pairs)), items)
    return _ir_label(label, control_id, body)


def multiselect(name, options, value=None, label=None, size=5):
    """A list in which several options may be chosen; the state value is a list."""
    pairs = _ir_options(options)
    current = _ir_default(name, list(value or []))
    control_id = 'cn-' + name
    items = ''.join('<option value="%s"%s>%s</option>' % (esc(v), ' selected' if v in (current or []) else '', esc(c)) for v, c in pairs)
    body = '<select multiple %s>%s</select>' % (_ir_attrs(
        id=control_id, class_='cn-input', size=size, data_cn_bind=name, data_cn_type='multi:' + _ir_option_type(pairs)), items)
    return _ir_label(label, control_id, body)


def radio(name, options, value=None, label=None, inline=True):
    """A group of radio buttons."""
    pairs = _ir_options(options)
    current = _ir_default(name, value if value is not None else (pairs[0][0] if pairs else None))
    control_id = 'cn-' + name
    kind = _ir_option_type(pairs)
    items = ''.join('<label class="cn-choice"><input type="radio" name="%s" value="%s"%s/> %s</label>'
                    % (control_id, esc(v), ' checked' if v == current else '', esc(c)) for v, c in pairs)
    body = '<div %s>%s</div>' % (_ir_attrs(id=control_id, class_='cn-radio' + (' cn-inline' if inline else ''),
                                           data_cn_bind=name, data_cn_type=kind), items)
    return _ir_label(label, control_id, body)


def checkbox(name, label='', value=False):
    """A check box; the state value is True or False."""
    current = bool(_ir_default(name, bool(value)))
    control_id = 'cn-' + name
    return Html('<label class="cn-choice cn-field"><input type="checkbox" %s/> %s</label>' % (_ir_attrs(
        id=control_id, checked=current, data_cn_bind=name, data_cn_type='bool'), esc(label)))


def toggle(name, label='', value=False):
    """An on/off switch; the state value is True or False."""
    current = bool(_ir_default(name, bool(value)))
    control_id = 'cn-' + name
    return Html('<label class="cn-toggle cn-field"><input type="checkbox" %s/><span class="cn-toggle-track"></span> %s</label>' % (_ir_attrs(
        id=control_id, checked=current, data_cn_bind=name, data_cn_type='bool'), esc(label)))


def date_input(name, value=None, label=None):
    """A date picker; the state value is an ISO date string ('2026-10-05')."""
    if value is not None and hasattr(value, 'isoformat'):
        value = value.isoformat()[:10]
    current = _ir_default(name, value or '')
    control_id = 'cn-' + name
    body = '<input type="date" %s/>' % _ir_attrs(id=control_id, class_='cn-input', value=current, data_cn_bind=name, data_cn_type='text')
    return _ir_label(label, control_id, body)


def color_input(name, value='#3366cc', label=None):
    """A colour picker; the state value is '#rrggbb'."""
    current = _ir_default(name, value)
    control_id = 'cn-' + name
    body = '<input type="color" %s/>' % _ir_attrs(id=control_id, class_='cn-color', value=current, data_cn_bind=name, data_cn_type='text')
    return _ir_label(label, control_id, body)


def button(label, action=None, call=None, kind='primary', confirm=None, disabled=False):
    """A button. action= fires one of the report's actions (an output of the block); call= runs a
    method of the report and renders the page again."""
    return Html('<button type="button" %s>%s</button>' % (_ir_attrs(
        class_='cn-button cn-' + kind, data_cn_action=action, data_cn_call=call, data_cn_confirm=confirm,
        disabled=bool(disabled)), esc(label)))


# ── Displays ──────────────────────────────────────────────────────────────────

def table(rows=None, columns=None, page_size=20, height=None, sortable=True, filter=True, select=None,
          formats=None, max_rows=20000, id=None):
    """A table with sorting, filtering and pages. select= names a state value that receives the
    clicked row as a dictionary."""
    headers, cells = _ir_table(_ir_data(rows), columns)
    total = len(cells)
    cells = cells[:max_rows] if max_rows else cells
    if select:
        _ir_default(select, None)
    spec = {
        'columns': headers, 'rows': cells, 'total': total, 'pageSize': page_size,
        'sortable': sortable, 'filter': filter, 'select': select, 'formats': formats or {},
    }
    style = 'max-height:%dpx' % height if height else None
    return Html('<div %s><script type="application/json">%s</script></div>' % (_ir_attrs(
        id=id or _ir_next_id('table'), class_='cn-table', data_cn_table='1', data_cn_opaque='1', style=style),
        _ir_json_block(spec)))


_IR_PALETTE = ['#3366cc', '#dc3912', '#ff9900', '#109618', '#990099', '#0099c6', '#dd4477', '#66aa00', '#b82e2e', '#316395']


def _ir_series(data, keys):
    if keys is None:
        return []
    if isinstance(keys, str):
        return [(keys, column(data, keys))]
    keys = keys.tolist() if hasattr(keys, 'tolist') else list(keys)
    if keys and all(isinstance(k, str) for k in keys) and data is not None:
        return [(k, column(data, k)) for k in keys]
    if keys and all(isinstance(k, (list, tuple)) or hasattr(k, 'tolist') for k in keys):
        return [('Series %d' % (i + 1), column(None, k)) for i, k in enumerate(keys)]
    return [('', keys)]


def chart(kind='line', data=None, x=None, y=None, labels=None, values=None, z=None, title='', height=360,
          colors=None, x_title=None, y_title=None, legend=True, stacked=False, size=None, text=None,
          min=None, max=None, layout=None, id=None, **trace):
    """A chart drawn with Plotly. kind: line, bar, barh, area, scatter, bubble, pie, donut,
    histogram, box, violin, heatmap, funnel, waterfall, radar, treemap, sunburst, gauge,
    indicator, candlestick. x/y/labels/values/z take column names of data or sequences; y may be
    a list of column names to draw several series."""
    data = _ir_data(data)
    kind = (kind or 'line').lower()
    palette = list(colors) if colors else _IR_PALETTE
    traces = []

    if kind in ('pie', 'donut', 'funnel', 'treemap', 'sunburst', 'funnelarea'):
        names = column(data, labels if labels is not None else x)
        amounts = column(data, values if values is not None else y)
        if kind in ('pie', 'donut'):
            t = {'type': 'pie', 'labels': names, 'values': amounts, 'marker': {'colors': palette}, 'sort': False}
            if kind == 'donut':
                t['hole'] = 0.5
        elif kind == 'funnel':
            t = {'type': 'funnel', 'y': names, 'x': amounts, 'marker': {'color': palette[0]}}
        else:
            t = {'type': kind, 'labels': names, 'values': amounts}
            parents = trace.pop('parents', None)
            t['parents'] = column(data, parents) if parents is not None else [''] * len(names or [])
        traces.append(t)
    elif kind in ('histogram',):
        for i, (name, series) in enumerate(_ir_series(data, x if x is not None else y)):
            traces.append({'type': 'histogram', 'x': series, 'name': name, 'marker': {'color': palette[i % len(palette)]}})
    elif kind in ('box', 'violin'):
        for i, (name, series) in enumerate(_ir_series(data, y if y is not None else x)):
            traces.append({'type': kind, 'y': series, 'name': name, 'marker': {'color': palette[i % len(palette)]}})
    elif kind == 'heatmap':
        matrix = z
        if isinstance(matrix, str):
            matrix = column(data, matrix)
        if matrix is None and data is not None:
            matrix = data.values.tolist() if hasattr(data, 'values') and hasattr(data, 'columns') else data
        t = {'type': 'heatmap', 'z': _ir_plain(matrix), 'colorscale': trace.pop('colorscale', 'RdYlGn')}
        if x is not None:
            t['x'] = column(data, x) if isinstance(x, str) else list(x)
        elif hasattr(data, 'columns'):
            t['x'] = [str(c) for c in data.columns]
        if y is not None:
            t['y'] = column(data, y) if isinstance(y, str) else list(y)
        traces.append(t)
    elif kind == 'radar':
        theta = column(data, labels if labels is not None else x)
        for i, (name, series) in enumerate(_ir_series(data, values if values is not None else y)):
            traces.append({'type': 'scatterpolar', 'r': series + series[:1], 'theta': theta + theta[:1], 'fill': 'toself',
                           'name': name, 'line': {'color': palette[i % len(palette)]}})
    elif kind in ('gauge', 'indicator'):
        amount = values if values is not None else y
        amount = column(data, amount)[-1] if isinstance(amount, str) else amount
        t = {'type': 'indicator', 'value': amount, 'title': {'text': title}}
        if kind == 'gauge':
            low = 0 if min is None else min
            high = 100 if max is None else max
            t['mode'] = 'gauge+number'
            t['gauge'] = {'axis': {'range': [low, high]}, 'bar': {'color': palette[0]}}
        else:
            t['mode'] = 'number'
        traces.append(t)
        title = ''
    elif kind == 'candlestick':
        t = {'type': 'candlestick', 'x': column(data, x)}
        for part in ('open', 'high', 'low', 'close'):
            t[part] = column(data, trace.pop(part, part))
        traces.append(t)
    elif kind == 'waterfall':
        traces.append({'type': 'waterfall', 'x': column(data, x), 'y': column(data, y)})
    else:
        xs = column(data, x)
        for i, (name, series) in enumerate(_ir_series(data, y)):
            color = palette[i % len(palette)]
            if kind in ('bar', 'barh', 'stacked_bar'):
                t = {'type': 'bar', 'name': name, 'marker': {'color': color}}
                if kind == 'barh':
                    t.update({'orientation': 'h', 'x': series, 'y': xs})
                else:
                    t.update({'x': xs, 'y': series})
            elif kind in ('scatter', 'bubble'):
                t = {'type': 'scatter', 'mode': 'markers', 'x': xs, 'y': series, 'name': name, 'marker': {'color': color}}
                if size is not None:
                    sizes = column(data, size)
                    # min and max are parameters here, so the builtin is reached by another name.
                    top = float(_ir_builtin_max(sizes) if sizes else 1.0) or 1.0
                    t['marker']['size'] = [6 + 40 * float(s) / top for s in sizes]
            else:
                t = {'type': 'scatter', 'mode': 'lines+markers' if kind == 'line' else 'lines', 'x': xs, 'y': series,
                     'name': name, 'line': {'color': color}}
                if kind == 'area':
                    t['fill'] = 'tonexty' if stacked and i else 'tozeroy'
                    if stacked:
                        t['stackgroup'] = 'one'
            if text is not None:
                t['text'] = column(data, text)
            traces.append(t)

    for t in traces:
        t.update(trace)
    spec_layout = {
        'title': {'text': title} if title else None,
        'height': height,
        'margin': {'l': 50, 'r': 20, 't': 50 if title else 20, 'b': 40},
        'showlegend': bool(legend) and len(traces) > 1 or (legend and kind in ('pie', 'donut')),
        'barmode': 'stack' if stacked or kind == 'stacked_bar' else 'group',
        'xaxis': {'title': {'text': x_title}} if x_title else {},
        'yaxis': {'title': {'text': y_title}} if y_title else {},
        'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)',
    }
    if layout:
        spec_layout.update(layout)
    return plotly({'data': traces, 'layout': {k: v for k, v in spec_layout.items() if v is not None}}, height=height, id=id)


def _ir_builtin_max(values):
    import builtins
    return builtins.max(values)


def plotly(figure, height=None, id=None, config=None):
    """Any Plotly figure: a plotly.graph_objects Figure or a {'data': [...], 'layout': {...}} dictionary."""
    spec = figure.to_plotly_json() if hasattr(figure, 'to_plotly_json') else dict(figure)
    spec.setdefault('layout', {})
    if height:
        spec['layout'].setdefault('height', height)
    spec['config'] = dict({'displaylogo': False, 'responsive': True}, **(config or {}))
    box_height = spec['layout'].get('height') or 360
    return Html('<div %s><script type="application/json">%s</script></div>' % (_ir_attrs(
        id=id or _ir_next_id('chart'), class_='cn-chart', data_cn_chart='1', data_cn_opaque='1',
        style='min-height:%dpx' % box_height), _ir_json_block(spec)))


def figure(fig, width=None, dpi=110):
    """A matplotlib figure, as a picture."""
    buffer = _ir_io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=dpi)
    try:
        import matplotlib.pyplot as plt
        plt.close(fig)
    except Exception:
        pass
    return image(buffer.getvalue(), width=width)


def image(source, width=None, alt=''):
    """A picture: bytes, a file path, or a URL."""
    if isinstance(source, (bytes, bytearray)):
        kind = 'jpeg' if bytes(source[:3]) == b'\xff\xd8\xff' else 'png'
        src = 'data:image/%s;base64,%s' % (kind, _ir_base64.b64encode(bytes(source)).decode('ascii'))
    elif isinstance(source, str) and _ir_os.path.isfile(source):
        extension = _ir_os.path.splitext(source)[1].lower().lstrip('.') or 'png'
        mime = {'jpg': 'jpeg', 'svg': 'svg+xml'}.get(extension, extension)
        with open(source, 'rb') as handle:
            src = 'data:image/%s;base64,%s' % (mime, _ir_base64.b64encode(handle.read()).decode('ascii'))
    else:
        src = str(source)
    style = 'width:%s' % (width if isinstance(width, str) else '%dpx' % width) if width else None
    return Html('<img %s/>' % _ir_attrs(class_='cn-image', src=src, alt=alt, style=style))


_IR_DEFAULT_SCALE = ['#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850']


def color_bar(value, min=0, max=100, colors=None, label=None, show_value=True, format=None, height=14, ticks=True):
    """A colour scale with a marker at the value — red to green by default."""
    scale = list(colors) if colors else _IR_DEFAULT_SCALE
    try:
        position = (float(value) - float(min)) / (float(max) - float(min)) * 100.0
    except (TypeError, ValueError, ZeroDivisionError):
        position = 0.0
    position = 0.0 if position != position else position
    position = 0.0 if position < 0 else 100.0 if position > 100 else position
    gradient = 'linear-gradient(to right, %s)' % ', '.join(scale)
    caption = '<div class="cn-label">%s%s</div>' % (
        esc(label or ''), (' <b>%s</b>' % esc(fmt(value, format) if format else _ir_number(float(value)) if isinstance(value, (int, float)) else value)) if show_value else '')
    marks = ('<div class="cn-colorbar-ticks"><span>%s</span><span>%s</span></div>' % (esc(min), esc(max))) if ticks else ''
    return Html('<div class="cn-colorbar cn-field">%s<div class="cn-colorbar-track" style="height:%dpx;background:%s">'
                '<div class="cn-colorbar-marker" style="left:%.2f%%"></div></div>%s</div>'
                % (caption, height, gradient, position, marks))


def progress(value, max=100, label=None, color=None, format=None):
    """A progress bar."""
    try:
        share = float(value) / float(max) * 100.0
    except (TypeError, ValueError, ZeroDivisionError):
        share = 0.0
    share = 0.0 if share < 0 else 100.0 if share > 100 else share
    style = 'width:%.2f%%%s' % (share, ';background:%s' % color if color else '')
    caption = '<div class="cn-label">%s <b>%s</b></div>' % (esc(label or ''), esc(fmt(value, format) if format else '%.0f%%' % share))
    return Html('<div class="cn-progress cn-field">%s<div class="cn-progress-track"><div class="cn-progress-fill" style="%s"></div></div></div>'
                % (caption, style))


def kpi(label, value, delta=None, format=None, delta_format=None, good='up', color=None):
    """A headline figure with an optional change beside it."""
    shown = fmt(value, format) if format else (_ir_number(value) if isinstance(value, float) else value)
    change = ''
    if delta is not None:
        try:
            positive = float(delta) >= 0
        except (TypeError, ValueError):
            positive = True
        tone = 'cn-good' if positive == (good == 'up') else 'cn-bad'
        arrow = '▲' if positive else '▼'
        change = '<div class="cn-kpi-delta %s">%s %s</div>' % (tone, arrow, esc(fmt(delta, delta_format) if delta_format else delta))
    style = ' style="border-top-color:%s"' % esc(color) if color else ''
    return Html('<div class="cn-kpi"%s><div class="cn-kpi-label">%s</div><div class="cn-kpi-value">%s</div>%s</div>'
                % (style, esc(label), esc(shown), change))


def badge(text, color='#3366cc'):
    """A small coloured label."""
    return Html('<span class="cn-badge" style="background:%s">%s</span>' % (esc(color), esc(text)))
