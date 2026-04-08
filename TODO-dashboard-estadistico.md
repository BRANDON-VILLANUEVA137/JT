# TODO: Dashboard Estadístico Admin (Panel Completo con PDF)

**Estado: [IN PROGRESS]**

## Pasos del Plan (Breakdown):

1. **[PENDING]** Breakdown approved: Create this TODO.md ✅
2. **[PENDING]** Read & analyze additional dependent files if needed (e.g. full pedidos/views.py, requirements.txt)
3. **[✅ DONE]** Update `usuarios/views.py`: Add comprehensive stats queries, date filters, JSON data for charts
4. **[✅ DONE]** Update `usuarios/templates/usuarios/dashboard_admin.html`: Add sections, charts, filters, PDF export JS, 8 KPIs, hero filters, CDNs
5. **[PENDING]** Test queries/data in shell (`python manage.py shell`)
6. **[PENDING]** Full test: Load dashboard, filter dates, charts interactive, PDF export
7. **[DONE]** Attempt completion
5. **[PENDING]** Add CDNs (Chart.js, jsPDF, html2canvas) to template
6. **[PENDING]** Test queries/data in shell (`python manage.py shell`)
7. **[PENDING]** Full test: Load dashboard, filter dates, charts interactive, PDF export
8. **[DONE]** Attempt completion

**Notas:**
- No migrations needed (use existing models)
- CDNs: No `pip install`
- Responsive: Extend existing Bootstrap/CSS

**Próximo paso:** Update backend views.py
