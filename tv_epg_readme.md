# TV EPG Scraper & Smart JSON Generator

Kjo skriptë përdor **Python** për të nxjerrë të dhëna mbi programet televizive nga [tvepg.eu](https://tvepg.eu) dhe për të gjeneruar JSON files për shtete të caktuara, për analizë dhe përdorim të mëtejshëm.

---

## Karakteristikat kryesore

- Nxjerr **link-et e shteteve** dhe **kanaleve televizive**.
- Mbledh të dhëna për **programet e televizionit** për ditë të caktuara.
- Gjeneron JSON files me:
  - Orarin e filimit dhe përfundimit të programeve.
  - Preferencat për kohën e zhanreve.
  - Blloqe prioritare për kanalet.
  - Informacion të detajuar mbi kanalet dhe programet.
- Mundëson **zgjedhjen e shtetit** dhe **numrin e ditëve** për të marrë të dhëna mbi guidat televizive.

---

## Si të përdoret

### 1. Instaloni paketat

```bash
pip install requests beautifulsoup4
```

### 2. Ekzekutoni skriptën

```bash
python world3.py
```

### 3. Zgjidhni një shtet nga lista

```
1. United Kingdom
2. Ireland
3. Germany
4. France
5. Italy
6. Spain
7. Portugal
8. Netherlands
9. Belgium
10. Austria
11. Luxembourg
12. Switzerland
13. Greece
14. Cyprus
15. Denmark
16. Norway
17. Sweden
18. Finland
19. Estonia
20. Latvia
21. Lithuania
22. Poland
23. Czechia
24. Slovakia
25. Hungary
26. Romania
27. Bulgaria
28. Croatia
29. Slovenia
30. North Macedonia
31. Bosnia and Herzegovina
32. Serbia
33. Albania
34. Ukraine
35. Russia
36. Turkey
```

### 4. Vendosni numrin e ditëve

P.sh., `7` për javën e ardhshme.

### 5. Skripta gjeneron JSON për çdo ditë

---

## Struktura e JSON-it

```json
{
  "opening_time": 360,
  "closing_time": 1380,
  "channels": [
    {
      "name": "BBC One",
      "id": "bbc_one",
      "shows": [
        {
          "title": "News at Six",
          "genre": "News",
          "start_time": "18:00",
          "end_time": "18:30"
        },
        {
          "title": "Drama Series",
          "genre": "Drama",
          "start_time": "18:30",
          "end_time": "19:30"
        }
      ]
    }
  ]
}
```

---

