# Notatki o biznesie: Micron Technology (MU), rok obrotowy FY2026 (do 3.09.2026)

Dokumenty 10-K (doc-017), DEF 14A (doc-018), 8-K (doc-019) i komunikat wynikowy (doc-020) są plikami HTML bez podziału na strony. Przy każdym fakcie podaję więc część dokumentu i numer strony wg numeracji drukowanej w 10-K. Liczby występują jako id propozycji w `D/propozycje.json` (73 propozycje, wszystkie przeszły test cytatu).

## Jak działa firma

- Micron jest producentem pamięci DRAM, NAND i NOR dla centrów danych, telefonów, komputerów, samochodów i urządzeń wbudowanych. [doc-017, Item 1, s. 7] „We are a global leader in semiconductor memory and storage, powering AI and compute-intensive applications from cloud to edge.”
- Spółka produkuje we własnych fabrykach i część procesów zleca podwykonawcom. [doc-017, Item 1, s. 7] „We manufacture our products at wholly-owned facilities and also utilize subcontractors for certain manufacturing processes.”
- Przychody DRAM wyniosły `{{przychody_dram.FY2026}}`, a przychody NAND `{{przychody_nand.FY2026}}` w FY2026. [doc-017, Item 1, s. 8] „Total reported DRAM revenue was $100.68 billion in 2026” oraz „Total reported NAND revenue was $31.79 billion in 2026”.
- Przychody to wolumen razy cena, a w FY2026 wzrosły głównie przez cenę. [doc-017, Item 7, s. 56] „Sales of DRAM products increased 252% primarily due to an approximate 180% increase in average selling prices and a mid-20% range increase in bit shipments.”
- Dla NAND było podobnie. [doc-017, Item 7, s. 56] „Sales of NAND products increased 274% primarily due to an approximate 200% increase in average selling prices and a mid-20% range increase in bit shipments.”
- Zarząd opisuje popyt jako większy od podaży. [doc-017, Item 7, s. 55] „AI-driven memory and storage demand growth is outpacing industry supply.”
- Zarząd przesunął podaż DRAM do centrów danych, kosztem innych klientów. [doc-017, Item 7, s. 55] „This has led to decisions on supply allocation that may impact certain customers and end markets.”
- Rynek centrów danych dawał około 60% przychodów (`{{udzial_centrum_danych.FY2026}}`). [doc-017, Item 1A, s. 33] „Among our end markets, approximately 60% of our total revenue was concentrated in the data center end market.”
- Koszt produkcji zależy od technologii i uzysku. [doc-017, Item 1, s. 13] „The primary determinants of manufacturing cost are process line-width, 3D non-volatile layers, NAND cell levels, process complexity (including the number of mask layers and fabrication steps), and manufacturing yield.”
- Produkcja jest kapitałochłonna. [doc-017, Item 1, s. 13] „Semiconductor manufacturing is capital intensive, requiring large investments in sophisticated facilities and equipment.”
- Spółka wchodzi w technologię 1-gamma (pierwszy węzeł DRAM z EUV) i HBM4. [doc-017, Item 1, s. 7–9] „In 2025, we began shipping the industry’s first 1γ (1-gamma) production node, which is our first DRAM node incorporating EUV lithography” oraz „In 2026, we began volume production of our HBM4 36GB 12-high”.
- Rozwój HBM4E zależy od węzła 1-gamma i ma ruszyć w 2027 roku. [doc-017, Item 1, s. 9] „Development of HBM4E, our next-generation HBM product leveraging our 1γ DRAM technology node, is well underway, and we expect to ramp volume in calendar 2027.”
- Zarząd zapowiada, że kontrakty strategiczne podniosą stabilność marż. [doc-017, Item 7, s. 55] „We expect gross margins from our strategic customer agreements with price bands, even at floor pricing levels, to yield gross margins meaningfully above our peak quarterly margins in any past cycle.”
- Spółka wycofała się ze sprzedaży detalicznej pod marką Crucial. [doc-017, Item 1, s. 10] „Our consumer products were sold under the brand name Crucial until an exit of that portion of our business was announced in December 2025.”
- Zatrudnienie wynosi `{{liczba_pracownikow.2026-09-03}}` osób. [doc-017, Item 1, s. 16] „As of September 3, 2026, we had approximately 61,000 employees located primarily in Asia, North America, and Europe.”
- Prognoza na 1Q FY2027: przychody `{{prognoza_firmy_przychody_1q_fy2027.brak}}` (± 1,5 mld USD). [doc-020, tabela „Business Outlook”] „Revenue $61.5 billion ± $1.5 billion”.

## Segmenty i KPI

Segmenty to jednostki biznesowe oparte na rynkach docelowych. Tabele z MD&A. [doc-017, Item 7, s. 57]

- CMBU (pamięci dla hiperskalerów i HBM dla wszystkich klientów centrów danych): przychody `{{przychody_segmentu_cmbu.FY2026}}`, udział `{{udzial_segmentu_cmbu.FY2026}}` (rok wcześniej `{{udzial_segmentu_cmbu.FY2025}}`), zysk operacyjny `{{zysk_operacyjny_segmentu_cmbu.FY2026}}`, marża operacyjna `{{marza_operacyjna_segmentu_cmbu.FY2026}}`. „CMBU $ 43,085 32 % $ 13,524 36 % $ 3,792 15 %” oraz „CMBU $ 31,225 72 % $ 6,129 45 % $ 244 6 %”. Opis: [doc-017, Item 1, s. 9] „CMBU is focused on memory solutions for large hyperscale cloud customers, and HBM for all data center customers.”
- CDBU (SSD i NAND dla centrów danych, DRAM dla OEM, przedsiębiorstw i NeoCloud): przychody `{{przychody_segmentu_cdbu.FY2026}}`, udział `{{udzial_segmentu_cdbu.FY2026}}` (rok wcześniej `{{udzial_segmentu_cdbu.FY2025}}`), zysk operacyjny `{{zysk_operacyjny_segmentu_cdbu.FY2026}}`, marża operacyjna `{{marza_operacyjna_segmentu_cdbu.FY2026}}`. „CDBU 37,592 28 % 7,229 19 % 4,984 20 %” oraz „CDBU 29,539 79 % 2,180 30 % 255 5 %”. Opis: [doc-017, Item 1, s. 9] „CDBU is focused on storage solutions for all data center customers, including data center SSDs and NAND components”.
- MCBU (telefony, komputery, komponenty): przychody `{{przychody_segmentu_mcbu.FY2026}}`, udział `{{udzial_segmentu_mcbu.FY2026}}` (rok wcześniej `{{udzial_segmentu_mcbu.FY2025}}`), zysk operacyjny `{{zysk_operacyjny_segmentu_mcbu.FY2026}}`, marża operacyjna `{{marza_operacyjna_segmentu_mcbu.FY2026}}`. „MCBU 36,601 27 % 11,859 32 % 11,667 46 %” oraz „MCBU 29,208 80 % 1,981 17 % (1) — %”. Opis: [doc-017, Item 7, s. 57] „MCBU revenue increased 209% primarily due to increases in average selling prices, partially offset by lower bit shipments as MCBU product supply was redirected to other business units.”
- AEBU (motoryzacja, przemysł, urządzenia wbudowane): przychody `{{przychody_segmentu_aebu.FY2026}}`, udział `{{udzial_segmentu_aebu.FY2026}}` (rok wcześniej `{{udzial_segmentu_aebu.FY2025}}`), zysk operacyjny `{{zysk_operacyjny_segmentu_aebu.FY2026}}`, marża operacyjna `{{marza_operacyjna_segmentu_aebu.FY2026}}`. „AEBU 15,886 12 % 4,753 13 % 4,631 18 %” oraz „AEBU 11,217 71 % 557 12 % 432 9 %”.
- Zysk operacyjny segmentów w FY2025 (porównanie): CMBU `{{zysk_operacyjny_segmentu_cmbu.FY2025}}`, CDBU `{{zysk_operacyjny_segmentu_cdbu.FY2025}}`, MCBU `{{zysk_operacyjny_segmentu_mcbu.FY2025}}`, AEBU `{{zysk_operacyjny_segmentu_aebu.FY2025}}` (marże: `{{marza_operacyjna_segmentu_cmbu.FY2025}}`, `{{marza_operacyjna_segmentu_cdbu.FY2025}}`, `{{marza_operacyjna_segmentu_mcbu.FY2025}}`, `{{marza_operacyjna_segmentu_aebu.FY2025}}`). [doc-017, Item 7, s. 57] te same wiersze tabeli „Operating Income (Loss) by Business Unit”.
- Wzrost zysku operacyjnego we wszystkich segmentach wynikał głównie z cen. [doc-017, Item 7, s. 57] „Operating income was higher for each business unit in 2026 as compared to 2025 primarily due to increases in average selling prices.”
- Komunikat wynikowy pokazuje, że w 4Q FY2026 marże operacyjne segmentów były wyższe niż średnia roczna. [doc-020, „Quarterly Business Unit Financial Results”] Blok MCBU kończy się wierszem „Operating margin 88 %”, a blok CDBU wierszem „Operating margin 85 %”. Liczb kwartalnych nie dodałem jako propozycji.
- Prognoza kwartalna: marża brutto około 85,95% (GAAP) w 1Q FY2027. [doc-020] „Gross margin Approximately 85.95%”.

## Klienci i dostawcy

- Połowa przychodów pochodzi od dziesięciu największych klientów. [doc-017, Item 1, s. 12] „In each of the last three years, approximately one-half of our total revenue was from our top ten customers.” W czynnikach ryzyka: [doc-017, Item 1A, s. 33] „In 2026, over half of our total revenue came from our top ten customers.”
- W FY2026 żaden klient nie przekroczył 10% przychodów. [doc-017, Note 21, s. 94] „No customer accounted for 10% or more of total revenue in 2026.”
- W FY2025 jeden klient dał `{{udzial_najwiekszego_klienta.FY2025}}` przychodów (głównie CMBU), a w FY2024 `{{udzial_najwiekszego_klienta.FY2024}}`. [doc-017, Note 21, s. 94] „Revenue from one customer was 17% (primarily included in the CMBU segment) of total revenue for 2025.”
- Nazwy największych klientów nie są ujawnione w 10-K ani w komunikacie (nazwa NVIDIA nie pada w doc-017).
- Spółka sprzedaje przez własny zespół sprzedaży, dystrybutorów i przedstawicieli. [doc-017, Item 1, s. 12] „We market our semiconductor memory and storage products primarily through our own direct sales force”.
- Umowy ze zwykłymi klientami są krótkie, a płatność następuje szybko. [doc-017, Item 1, s. 12] „Contracts with certain of our customers are short-term in duration.” oraz „For all of our contracts, payments are generally due shortly after delivery.”
- Strategic Customer Agreements (SCA) mają formę take-or-pay z wielokrotnością lat. [doc-017, Item 1, s. 12] „We also have strategic customer agreements structured as take-or-pay agreements, with binding commitments for specific contractually enforceable volumes over the multi-year contract terms.”
- Większość SCA ma ceny w pasmach minimum–maksimum. [doc-017, Item 1, s. 12] „with the majority of the strategic customer agreements having pricing that is subject to minimum and maximum bands.”
- Spółka zawarła SCA w 3Q i 4Q FY2026 i spodziewa się kolejnych. [doc-017, Item 7, s. 55] „In the third and fourth quarters of 2026, we entered into, and expect to continue to enter into, strategic customer agreements.”
- Pozostałe zobowiązania do wykonania (RPO) wynoszą `{{rpo.2026-09-03}}`, z czego `{{rpo_zobowiazania_umowne.2026-09-03}}` to zobowiązania umowne (depozyty). [doc-017, Note o przychodach, s. 88] „the transaction price allocated to our remaining performance obligations was approximately $134 billion, of which $13 billion has been recognized as contract liabilities.”
- Około jedna czwarta RPO ma zostać rozpoznana w 12 miesięcy, a całość w pięć lat. [doc-017, s. 88] „Approximately one-fourth of the remaining performance obligations as of September 3, 2026 are expected to be recognized as revenue over the next twelve months. The remaining performance obligations are expected to be fully recognized within the next five years.”
- RPO nie wskazuje przyszłych przychodów i pomija umowy bez stałej ceny lub pasm. [doc-017, s. 88] „Our remaining performance obligations are based on expected purchases to satisfy committed volumes and minimum pricing and are not expected to be indicative of future revenue under these contracts.”
- Rok wcześniej RPO było nieistotne. [doc-017, s. 88] „As of August 28, 2025, our remaining performance obligations were not material.”
- Klienci wpłacili depozyty `{{depozyty_klientow_sca.FY2026}}`, które spółka ma w większości zwrócić w latach 2029–2031, jeśli klient spełni minimalne zakupy. [doc-017, Item 7, s. 59] „we received cash deposits of $12.75 billion in 2026. Nearly all of the deposits are scheduled to be repaid between 2029 and 2031.” oraz „Strategic customer agreements often include substantial customer deposits that are returned to the customer if the customer meets the minimum purchase commitments.”
- Klienci SCA dostarczyli akredytywy na `{{akredytywy_klientow.2026-09-03}}`. [doc-017, Item 7, s. 59] „The aggregate amount of letters of credit issued, or contractually committed to be issued, by third-party financial institutions was $7 billion as of September 3, 2026.”
- Dostawcy: kilku dostawców dostarcza niektóre materiały, a część pochodzi z jednego źródła. [doc-017, Item 1, s. 14] „However, only a limited number of suppliers are capable of delivering certain materials, components, and services that meet our standards and, in some cases, materials, components, or services are provided by a single or sole source”.
- Spółka nie ma gwarancji pojemności ani cen od wielu dostawców. [doc-017, Item 1, s. 14] „many of these contracts do not provide for long-term capacity or pricing commitments.”
- Spółka płaci klientom korekty cen. [doc-017, Item 7, s. 62] „an increase in other current liabilities resulting mainly from higher consideration payable to customers for pricing adjustments”.

## Geografia i ekspozycja na Chiny

Przychody wg siedziby klienta. [doc-017, Note 22, s. 94] „Revenue based on the geographic location of our customers’ headquarters was as follows”.
- USA `{{przychody_geo_usa.FY2026}}`: „U.S. $ 91,323 $ 24,113 $ 13,168”.
- Tajwan `{{przychody_geo_tajwan.FY2026}}`: „Taiwan 16,950 5,672 4,708”.
- Chiny kontynentalne `{{przychody_geo_chiny.FY2026}}` (FY2025 `{{przychody_geo_chiny.FY2025}}`, FY2024 `{{przychody_geo_chiny.FY2024}}`): „Mainland China (excluding Hong Kong) 8,338 2,639 3,045”.
- Hongkong `{{przychody_geo_hongkong.FY2026}}` (FY2025 `{{przychody_geo_hongkong.FY2025}}`): „Hong Kong 6,289 1,138 1,071”.
- Udziały Chin i Hongkongu w przychodach powinien policzyć kod z id powyżej i `{{przychody.FY2026}}`; nie wpisuję procentów ręcznie.
- Decyzja CAC z maja 2023 nadal ogranicza sprzedaż do operatorów infrastruktury krytycznej w Chinach. [doc-017, Item 1A, s. 26] „Following the May 2023 decision of its cybersecurity review of our products sold in China, the CAC determined that critical information infrastructure operators in China may not purchase Micron products, impacting our revenue with companies headquartered in mainland China and Hong Kong, including direct sales, as well as indirect sales through distributors.”
- Kolejne działania rządu Chin mogą dotknąć przychody i operacje. [doc-017, Item 1A, s. 26] „Further actions by the Chinese government, through CAC action or other means, could impact revenue inside or outside China, or our operations in China, or our ability to ship products to our customers”.
- Spółka ma w Chinach montaż i testy (nie fabrykę wafli). [doc-017, Item 2, s. 49] „China Component assembly and test, module assembly and test”.
- USA ograniczają też sprzedaż do niektórych klientów. [doc-017, Item 1A, s. 26] „the U.S. government has in the past and continues to restrict U.S. firms, including us, from selling products and software to certain of our customers”.

## Produkcja i lokalizacje

- Większość produkcji DRAM w FY2026 pochodziła z Tajwanu. [doc-017, Item 1A, s. 27] „A majority of our DRAM production output in 2026 was from our fabrication facilities in Taiwan, and any loss of output could have a material adverse effect on us.”
- Aktywa trwałe wg lokalizacji: Tajwan `{{aktywa_trwale_geo_tajwan.2026-09-03}}`, USA `{{aktywa_trwale_geo_usa.2026-09-03}}`, razem `{{aktywa_trwale_geo_razem.2026-09-03}}`. [doc-017, Note 22, s. 94] „Taiwan $ 27,613 $ 18,965”, „U.S. 14,463 8,445”, „$ 64,031 $ 47,326”. Singapur, Japonia i Malezja są w tej samej tabeli (nie dodane jako propozycje).
- Fabryki wafli (wafer fabrication) działają na Tajwanie, w Singapurze, USA i Japonii. [doc-017, Item 2, s. 49] „Taiwan R&D, wafer fabrication, component assembly and test, module assembly and test Singapore R&D, wafer fabrication, component assembly and test, module assembly and test United States R&D, wafer fabrication, reticle manufacturing Japan R&D, wafer fabrication”.
- Spółka używa prawie całej obecnej mocy. [doc-017, Item 2, s. 49] „We generally utilize all of our existing manufacturing capacity.”
- Spółka kupiła fabrykę w Tongluo (Tajwan) od PSMC za `{{zakup_fabryki_tongluo.2026-03}}`. [doc-017, Item 7, s. 61] „In March 2026, we completed the acquisition of a wafer fabrication facility in Tongluo, Miaoli County, Taiwan, from Powerchip Semiconductor Manufacturing Corporation for cash consideration of $1.8 billion.”
- Spór pracowniczy: związki zawodowe prowadzą mediacje, które mogą dopuścić strajk. [doc-017, Item 1A, s. 38] „Labor unions representing a portion of our workforce have been engaged in union organizing and collective bargaining activities, including formal mediations (which, if not successful, could permit strike actions), and public demands for revised incentive structures.” (10-K nie nazywa lokalizacji ani „Fab 11E”).

## Plan capex, dotacje i nowe fabryki

- Plan capex netto (po dotacjach): `{{capex_plan_1q_fy2027.brak}}` w 1Q FY2027, `{{capex_plan_1h_fy2027.brak}}` w pierwszym półroczu, więcej w drugim. [doc-017, Item 7, s. 60] „We estimate capital expenditures for property, plant, and equipment, net of proceeds from government incentives, to be approximately $11.5 billion in the first quarter of 2027, approximately $25 billion in the first six months of 2027, and higher in the second half of 2027.”
- Capex netto w FY2026 wyniósł `{{capex_netto_firma.FY2026}}`, a skorygowany FCF `{{adjusted_fcf_firma.FY2026}}` (miara spółki, nie GAAP). [doc-020, akapit pod tabelą roczną] „Investments in capital expenditures, net(2) were $10.77 billion for the fourth quarter of 2026 and $27.37 billion for the full year of 2026.”
- Zobowiązania zakupowe na rzeczowe aktywa trwałe: `{{zobowiazania_zakupowe_ppe.2026-09-03}}`. [doc-017, Item 7, s. 60] „we had purchase obligations of approximately $4.18 billion for the acquisition of property, plant, and equipment”.
- Spółka potrzebuje nowej mocy DRAM w drugiej połowie dekady. [doc-017, Item 2, s. 49] „we will need to add new DRAM wafer capacity to support projected memory demand in the second half of the decade and beyond.”
- Idaho, fab 1: pierwsze wafle w połowie 2027. [doc-017, Item 7, s. 60] „Construction of the fab began in October 2023, with first DRAM wafer output projected in mid-calendar 2027.”
- Idaho, fab 2: pierwsze wafle pod koniec 2028. [doc-017, Item 7, s. 60] „Construction activities for the second Idaho fab began in 2026, and we expect initial wafer output by late calendar 2028.”
- Nowy Jork (Clay): do czterech fabryk w ciągu ponad 20 lat, pierwsze wafle w 2030. [doc-017, Item 7, s. 60] „consisting of up to four fabs to be built over the next 20-plus years, in Clay, New York” oraz „We expect initial wafer output in calendar 2030.”
- Hiroshima (Japonia): nowa hala czystych pomieszczeń, pierwsza produkcja pod koniec 2028. [doc-017, Item 7, s. 61] „we expect initial output in late calendar 2028”.
- Singapur: pakowanie HBM od początku 2027, nowa fabryka NAND w drugiej połowie 2028. [doc-017, Item 7, s. 61] „to meaningfully expand our total advanced packaging capacity beginning in early calendar 2027” oraz „operational in the second half of calendar 2028”.
- Tongluo: istniejąca fabryka ma dawać dostawy od połowy 2027, a spółka buduje drugą halę. [doc-017, Item 7, s. 61] „We expect this site to support meaningful product shipments from the existing fab beginning in mid-calendar 2027.”
- Dotacje CHIPS Act: `{{chips_dotacja_bezposrednia.brak}}` dla Idaho i Nowego Jorku oraz `{{chips_dotacja_manassas.brak}}` dla Manassas, razem `{{chips_dotacje_razem.brak}}`. [doc-017, Item 7, s. 60] „up to $6.1 billion in direct funding pursuant to the CHIPS Act” oraz „represent total CHIPS Act grants of up to $6.4 billion”.
- Ulga inwestycyjna CHIPS: `{{chips_ulga_inwestycyjna.brak}}`. [doc-017, Item 7, s. 60] „we receive a 35% investment tax credit on qualified investments in U.S. semiconductor manufacturing under the CHIPS Act.”
- Stan Nowy Jork: wstępne, niewiążące warunki do `{{nowy_jork_term_sheet.brak}}`. [doc-017, Item 7, s. 60] „We have also signed a non-binding term sheet with the State of New York that provides for up to $5.5 billion in funding”.
- Dotacje mogą zostać cofnięte. [doc-017, Item 7, s. 59] „Our incentives are conditioned upon achieving or maintaining certain outcomes and satisfying compliance requirements and are subject to reduction, termination, or clawback.”

## Konkurenci

- Lista konkurentów w 10-K: Samsung, SK hynix, Kioxia, Sandisk, CXMT i YMTC. [doc-017, Item 1, s. 12] „We face intense competition in the semiconductor memory and storage markets from a number of companies, including Samsung Electronics Co., Ltd.; SK hynix Inc.; Kioxia Holdings Corporation; Sandisk Corporation; ChangXin Memory Technologies, Inc. (“CXMT”); and Yangtze Memory Technologies Co., Ltd. (“YMTC”).”
- Konkurenci mogą mieć większy udział i zasoby oraz wsparcie państwa. [doc-017, Item 1, s. 12] „Some of our competitors are large corporations or conglomerates that may operate in jurisdictions with lower labor and compliance costs and may have a larger market share and greater resources to invest in technology”.
- Rządy wspierają część konkurentów, w tym CXMT i YMTC. [doc-017, Item 1, s. 12] „we face the threat of increasing competition and DRAM and NAND oversupply due to significant investment in the semiconductor industry, including by the Chinese government and various state-owned or affiliated entities, such as CXMT and YMTC.”
- Wszyscy producenci planują nowe moce. [doc-017, Item 1, s. 12] „We, and some of our competitors, have plans to construct new fabrication facilities and/or ramp production at existing fabrication facilities to increase supply in response to a significant increase in demand for memory products across the industry.”
- Zarząd przyznaje, że przy słabszym popycie ceny mogą spaść. [doc-017, Item 1, s. 12] „If worldwide demand for semiconductor memory and storage does not increase or remain stable, average selling prices for our products could decline materially”.
- Cel spółki: utrzymać stabilny udział w bitach. [doc-017, Item 2, s. 50] „our objective of maintaining stable bit share”.
- 10-K nie podaje miejsca Microna w rankingu DRAM ani udziałów rynkowych konkurentów.

## Kandydaci na przewagę konkurencyjną (korzyść i bariera)

Zbieram dowody, ocenę wydaje wątek główny.

1. Efektywna skala i przewaga procesowa (korzyść: niższy koszt bitu; bariera: kapitał i know-how).
   - Dowód na korzyść: [doc-017, Item 1, s. 7] „We continue to make significant investments to develop proprietary product and process technology, which generally increases bit density per wafer and reduces per-bit manufacturing costs of each generation of product.”
   - Dowód na barierę: [doc-017, Item 1, s. 13] „Semiconductor manufacturing is capital intensive, requiring large investments in sophisticated facilities and equipment.” Plan capex w sekcji wyżej.
   - Kontrdowód: konkurenci inwestują równolegle, a państwo wspiera część z nich (cytaty w sekcji „Konkurenci”). Spółka nie ujawnia kosztu bitu na tle konkurentów.
2. Koszty zmiany dostawcy przez kwalifikację produktów (korzyść: trwalsze relacje; bariera: czas kwalifikacji).
   - Dowód: [doc-017, Item 1, s. 11] „Collaborating with our customers on their design needs in changing end markets and meeting their timelines for qualifying new products allows us to differentiate our memory and storage solutions, which provides greater value to our customers.”
   - Dowód: [doc-020, Product Highlights] „We have completed multiple customer qualifications of our 1-gamma based, 8,800 MT/s high-speed server RDIMM modules.”
   - Kontrdowód: [doc-017, Item 1, s. 12] „Contracts with certain of our customers are short-term in duration.” oraz dystrybutorzy sprzedają także produkty konkurentów: „typically sell a variety of other semiconductor products, including our competitors’ products”.
3. Kontrakty take-or-pay z pasmami cen (korzyść: widoczność i niższa cykliczność, deklarowana przez zarząd; bariera: kapitał klientów w depozytach i akredytywy).
   - Dowód: cytaty o SCA w sekcji „Klienci i dostawcy” (depozyty `{{depozyty_klientow_sca.FY2026}}`, akredytywy `{{akredytywy_klientow.2026-09-03}}`, RPO `{{rpo.2026-09-03}}`).
   - Ograniczenia: umowy są świeże (RPO rok wcześniej nieistotne), a wiele umów ma ceny w pasmach, więc cena zależy od rynku w ramach pasma. Okres obowiązywania pojedynczych umów nie jest ujawniony poza „multi-year” i RPO w ciągu pięciu lat.
4. Aktywa niematerialne (patenty).
   - Nie zbierałem dowodów o liczbie i sile patentów. 10-K wspomina o ochronie własności intelektualnej tylko w czynnikach ryzyka. Do uzupełnienia, jeśli wątek główny uzna to za potrzebne.
5. Nie uznaję za przewagę: dużego udziału w rynku, szybkiego wzrostu przychodów (głównie z cen: [doc-017, Item 7, s. 56] „approximate 180% increase in average selling prices”) ani „jednego przebojowego produktu” (HBM).

Test cykliczności (dowody): zysk netto FY2023 jest ujemny w rejestrze faktów (`{{zysk_netto.FY2023}}`, doc-001, XBRL). W 10-K FY2026 jest tylko pośredni ślad tego roku. [doc-017, Item 7, s. 56] „Our consolidated gross margin for 2024 reflected $987 million of benefit due to lower costs from the sale of inventories written down to their net realizable value in 2023.” Zmienność cen to pierwszy czynnik ryzyka spółki. [doc-017, Item 1A, s. 23] „volatility in average selling prices of our products;”.

## Zarząd i alokacja kapitału

Zarząd. DEF 14A (doc-018) dotyczy FY2025 (zgromadzenie 15.01.2026); proxy za FY2026 nie jest jeszcze w archiwum.
- CEO Sanjay Mehrotra kieruje spółką od maja 2017 (około dziewięciu lat do daty analizy) i jest też prezesem rady od stycznia 2025. [doc-018, „Nominees”, s. 9] „Mr. Mehrotra has served as Micron’s President, Chief Executive Officer, and Director since May 2017 and has served as Micron’s Chairman since January 2025.”
- Poprzednio współtworzył i prowadził SanDisk. [doc-018, s. 9] „Mr. Mehrotra co-founded and led SanDisk Corporation as a start-up in 1988 until its eventual sale in May 2016”.
- Rada łączy funkcje prezesa i CEO, ale ma niezależnego głównego dyrektora. [doc-018, s. 6 i 50] „Our Board is currently led by Sanjay Mehrotra, as our Chairman, President and Chief Executive Officer, and Lynn A. Dugle, as our Lead Independent Director.” oraz „Seven of eight director nominees are independent”.
- Łączne wynagrodzenie CEO w FY2025: `{{wynagrodzenie_ceo_razem.FY2025}}`, w tym nagrody akcyjne około 25,4 mln USD. [doc-018, Summary Compensation Table, s. 65] „Sanjay Mehrotra 2025 $ 1,446,185 $ — $ 25,360,029 $ 3,894,990 $ 238,942 $ 30,940,146”. (Wynagrodzenie za FY2026 będzie w proxy 2026.)
- Wynagrodzenie opiera się na zyskowności, celach strategicznych i względnym zwrocie dla akcjonariuszy. [doc-018, s. 40] „using a balance of profitability and strategic metrics to incentivize stretching performance” oraz „outperformance on total shareholder return relative to our comparator group of the SOX index (“rTSR”) at the 55th percentile”.
- CEO ma wytyczną posiadania akcji o wartości sześciokrotności pensji. [doc-018, s. 59] „The minimum ownership guideline for our Chief Executive Officer is to hold shares with a value equal to six times his base salary.”
- Akcje CEO: `{{akcje_ceo.2025-10-31}}` (poniżej 1% kapitału). [doc-018, Security Ownership, s. 94] „Sanjay Mehrotra(7) 1,084,078 — 1,084,078”. Zarząd i dyrektorzy razem: `{{akcje_zarzad_i_dyrektorzy.2025-10-31}}`. „All directors and executive officers as a group (18 persons) 2,675,270 10,782 2,686,052”.
- Akcjonariusze powyżej 5%: Vanguard `{{udzial_vanguard.2025-10-31}}`, BlackRock `{{udzial_blackrock.2025-10-31}}` oraz Capital World Investors (6,3%, brak id propozycji). [doc-018, s. 94] „The Vanguard Group, Inc.(4) 94,984,500 — 94,984,500 8.4 %” oraz „BlackRock, Inc.(5) 85,904,256 — 85,904,256 7.6 %”. Brak akcjonariusza kontrolującego.
- Spółka zakazuje zastawiania i zabezpieczania akcji przez kadrę oraz ma politykę odzyskiwania premii. [doc-018, s. 41] „pledging or hedging activities involving our stock” (fragment listy dobrych praktyk) oraz „Maintain a compensation recoupment (“clawback”) policy”.
- Zmiana w radzie z 8-K z 5.11.2026: dyrektor Linnie Haynesworth rezygnuje z kandydowania i zostaje do końca kadencji na zgromadzeniu FY2026. [doc-019, pozycja 5.02] „Ms. Haynesworth notified the Governance and Sustainability Committee of the Board of Directors (the “Board”) of Micron Technology, Inc. (the “Company”) that she would retire from the Board and, accordingly, Ms. Haynesworth will not be nominated for re-election”. 8-K nie dotyczy zarządu wykonawczego ani wynagrodzeń.

Alokacja kapitału.
- Dywidenda: kwartalnie `{{dywidenda_kwartalna.2026-09-30}}` na akcję, spółka chce ją zwiększać. [doc-017, Item 5, s. 52–53] „On September 30, 2026, our Board of Directors declared a quarterly dividend of $0.15 per share” oraz „We currently expect quarterly dividends to continue in future periods and aim to grow our dividend payments over time.”
- Skup akcji w FY2026: `{{skup_akcji_program.FY2026}}` (2,5 mln akcji); w FY2025 brak skupu. [doc-017, Note 12, s. 83] „We repurchased 2.5 million shares of our common stock for $650 million in 2026. No shares were repurchased in 2025.”
- Nowe upoważnienie z 8.10.2026: łącznie `{{upowaznienie_skupu_calosc.2026-10-08}}`, obowiązujące od 9.12.2026, równe 100% skorygowanego FCF za 4Q FY2026 minus dywidendy plus resztka starego limitu (`{{upowaznienie_skupu_pozostalo.2026-09-03}}`). [doc-017, Item 5, s. 52–53] „authorized an increase in the amount authorized under this stock repurchase program for a total authorization of $35.16 billion” oraz „plus 100% of our adjusted free cash flow, less proceeds of CHIPS Act grant incentives received with respect to capital expenditures and less dividends paid”.
- Umowy CHIPS ograniczają skup. [doc-017, Item 5, s. 52–53] „stock repurchases are permitted during the first two years of the five-year period following the Idaho and New York award date of December 9, 2024, up to amounts specified in the funding agreements, to help offset the dilutive effects of employee stock compensation or as otherwise permitted by the U.S. Department of Commerce.” W kolejnych trzech latach skup podlega limitom opartym na FCF.
- Spółka spłaciła dług w FY2026. [doc-017, Cash flow, s. 70] „Repayments of debt (10,043) (4,619) (1,897)” (kwoty w mln USD, FY2026 pierwsza kolumna); w rejestrze są też pozycje dlug.
- Finansowanie z depozytów klientów: „Proceeds from customer contract liability deposits 12,747”. [doc-017, Cash flow, s. 70]
- Spółka planuje 10 mld USD na Micron Research Labs w dekadę. [doc-017, Item 7, s. 60] „supported by a planned investment of approximately $10 billion over the next decade”.
- Przejęcia: jedyna większa transakcja w FY2026 to zakup fabryki w Tongluo (sekcja „Produkcja”).

## Tropy

Źródło: D/tropy.md (InvestingPro, doc-016). Wyniki sprawdzenia w dokumentach spółki.

1. SCA, liczba, RPO do 2030, przedpłaty: potwierdzony w części [doc-017]: SCA, RPO `{{rpo.2026-09-03}}` rozpoznawane w pięć lat, depozyty `{{depozyty_klientow_sca.FY2026}}`. Liczba umów niepotwierdzona (10-K pisze „a number of customers”: „In 2026, we executed strategic customer agreements with a number of customers.”).
2. Udział zakontraktowanych dostaw w FY2027: niepotwierdzony. Jedyna pokrewna wartość to około jedna czwarta RPO do rozpoznania w 12 miesięcy [doc-017], co nie jest udziałem w dostawach.
3. HBM, wspólny projekt z NVIDIA (HBM4E/„NVHBM”): niepotwierdzony. 10-K nie zawiera nazwy NVIDIA ani „NVHBM”; potwierdza HBM4E na węźle 1-gamma z rozruchem w 2027 [doc-017]. Udział największego klienta: w FY2026 żaden powyżej 10%, w FY2025 `{{udzial_najwiekszego_klienta.FY2025}}` [doc-017].
4. Segmenty CMBU, CDBU, MCBU, AEBU: potwierdzony [doc-017] (sekcja „Segmenty i KPI”).
5. Chiny, spadek do jednocyfrowego udziału: potwierdzony co do danych [doc-017, Note 22]: przychody Chin kontynentalnych `{{przychody_geo_chiny.FY2026}}` wobec `{{przychody_geo_chiny.FY2025}}` rok wcześniej i `{{przychody_geo_chiny.FY2024}}` dwa lata wcześniej; udział do policzenia kodem. Ograniczenia CAC z 2023 roku potwierdzone [doc-017, Item 1A].
6. Micron trzecim producentem DRAM: niepotwierdzony. 10-K wymienia konkurentów, ale nie podaje rankingu ani udziałów.
7. Tajwan: potwierdzony w części. Większość produkcji DRAM z Tajwanu [doc-017]. Wstrzymanie budowy Fab 11E i spór pracowniczy z Bloomberga: niepotwierdzony w 10-K (brak nazwy „Fab 11E”); 10-K opisuje ogólnie mediacje związkowe i ryzyko strajku [doc-017, Item 1A]. Przyczyna spadku kursu: niesprawdzona (poza zakresem dokumentów).
8. CXMT, postęp w DRAM serwerowym: potwierdzony w części. CXMT jest wymieniony jako konkurent wspierany przez państwo chińskie [doc-017]; opis postępu w DRAM serwerowym nie występuje.
9. Capex i hale w Idaho, Nowym Jorku, Singapurze z bitami od 2028–2029: częściowo sprzeczny [doc-017]. Plan capex FY2027 potwierdzony (`{{capex_plan_1h_fy2027.brak}}` w pierwszym półroczu). Terminy: pierwsza fabryka Idaho ma dać wafle w połowie 2027, druga pod koniec 2028, Nowy Jork w 2030, więc „od 2028–2029” nie dotyczy pierwszej fabryki Idaho.
10. Cykliczność, FY2023 stratny: potwierdzony w rejestrze (`{{zysk_netto.FY2023}}`, doc-001) i pośrednio w [doc-017, Item 7, s. 56] (odpis zapasów w 2023). Szczyt marży brutto w FY2026: 10-K podaje marżę brutto 81% wobec 40% rok wcześniej; zarząd twierdzi, że SCA podniosą dołek marży, co zostaje deklaracją niezweryfikowaną w danych.
11. 8-K z 5.11.2026 (poz. 5.02): potwierdzony [doc-019]: rezygnacja dyrektora z kandydowania, bez zmian w zarządzie wykonawczym i wynagrodzeniach.
12. Konsensus EPS i cena docelowa z InvestingPro: niesprawdzony (poza zakresem tej notatki).
13. Arkusz ceny docelowej właściciela (doc-013): niesprawdzony (poza zakresem tej notatki).

## Czego nie znalazłem

- Nazw największych klientów i ich udziałów w FY2026 (10-K podaje tylko, że żaden nie przekroczył 10%).
- Liczby SCA, ich czasu trwania (poza „multi-year” i horyzontem pięciu lat dla RPO) oraz udziału zakontraktowanych dostaw w FY2027.
- Udziałów rynkowych DRAM, HBM i NAND oraz rankingu Microna; 10-K nie podaje danych o koncentracji branży (HHI nie da się policzyć z dokumentów).
- Informacji o Fab 11E, o wspólnym projekcie z NVIDIA i o przyczynach spadku kursu (poza archiwum).
- Szczegółów FY2023 poza rejestrem faktów: 10-K FY2026 obejmuje lata 2024–2026. Opis spadku cen i odpisów z 2023 wymaga 10-K FY2023 (nie pobierałem).
- Wynagrodzenia i akcji CEO za FY2026: DEF 14A dotyczy FY2025. Transkryptu rozmowy z inwestorami nie szukałem (nie jest w SEC).
- Liczby i siły patentów (nie zbierałem).
