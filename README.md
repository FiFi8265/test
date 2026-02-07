# Lista Zakupów (Android Studio) — kompletna specyfikacja i architektura

Poniższy dokument opisuje **spójną wizję produktu**, **architekturę kodu**, **model danych** oraz **plan integracji z Firebase** dla aplikacji listy zakupów dla gospodarstwa domowego. Założeniem jest **estetyczny, jednolity UI** (Material 3) i **szybka obsługa codziennych zakupów**.

## 1) Wizja produktu
- Jedna lista dla całego domu, współdzielona przez członków.
- Szybkie dodawanie pozycji i oznaczanie zakupów.
- Inteligentne sugestie na podstawie historii.
- Kontrola wydatków (miesięczne/roczne, kategorie).
- Offline-first: aplikacja działa bez Internetu, a dane synchronizują się później.

## 2) UX i spójność wizualna
- **Material 3** z własnym design system (kolory, typografia, spacing, ikony).
- Jednolite komponenty listy (karta produktu, status zakupu, badge kategorii).
- Czytelne stany: „do kupienia”, „w koszyku”, „kupione”.
- Subtelne animacje (odznaczanie, przesunięcie, grupowanie).

## 3) Funkcje kluczowe (MVP + bajery)
### MVP
- Lista zakupów z kategoriami.
- Dodawanie, edycja, usuwanie, oznaczanie jako kupione.
- Historia zakupów.
- Zapisywanie ceny zakupu.

### Bajery i rozszerzenia
- **Najczęściej kupowane**: ranking produktów + szybkie dodawanie.
- **Sugestie**: autouzupełnianie nazw i kategorii.
- **Statystyki**: miesięczne/roczne wydatki, podział na kategorie.
- **Budżety**: limit miesięczny + ostrzeżenia.
- **Powiadomienia**: przypomnienie o brakach (na podstawie cyklicznych zakupów).
- **Skanowanie kodów** (opcjonalnie): szybkie dodanie produktu.
- **Widok magazynu**: lista produktów „w domu” + planowane zakupy.

## 4) Proponowany stos technologiczny
- **Kotlin**
- **Jetpack Compose** (Material 3)
- **MVVM + Clean Architecture**
- **Room** (offline-first)
- **Firebase** (Auth + Firestore + Cloud Functions opcjonalnie)
- **Hilt** (DI)
- **WorkManager** (synchronizacja w tle)

## 5) Architektura (Clean Architecture + offline-first)
```
app/
  presentation/    -> Compose UI, ViewModel, UI state
  domain/          -> UseCase, Encje, Kontrakty repo
  data/            -> Repo implementacje, data sources
  core/            -> design system, utils, analytics
```

### Warstwy
1) **Presentation**
   - Ekrany Compose + komponenty UI (karty produktów, chips kategorii).
   - ViewModel obsługuje stan, filtrację i paginację list.
2) **Domain**
   - Encje: `ShoppingItem`, `Category`, `Purchase`, `Household`.
   - UseCase: `AddItem`, `ToggleBought`, `GetMonthlyStats`, `AddToFavorites`.
3) **Data**
   - `LocalDataSource` (Room).
   - `RemoteDataSource` (Firebase).
   - Repozytoria: logika synchronizacji i konfliktów.

## 6) Model danych (domena + Room)
### ShoppingItem
```
id: String
name: String
quantity: Double
unit: String?        // szt, kg, l
categoryId: String?
isBought: Boolean
lastPrice: Double?
createdAt: Long
updatedAt: Long
```

### Purchase (historia zakupów)
```
id: String
itemId: String
price: Double
date: Long
quantity: Double
```

### FavoriteItem (najczęstsze)
```
id: String
name: String
categoryId: String?
lastUsedAt: Long
count: Int
```

### Household
```
id: String
name: String
members: List<String> // UID z Firebase Auth
```

## 7) Schemat Firebase (propozycja)
```
households/{householdId}
  name: String
  members: [uid]

households/{householdId}/items/{itemId}
  name, quantity, unit, categoryId, isBought, lastPrice, updatedAt

households/{householdId}/purchases/{purchaseId}
  itemId, price, date, quantity

households/{householdId}/favorites/{favoriteId}
  name, categoryId, lastUsedAt, count
```

## 8) Synchronizacja (offline-first)
- Zapis w **Room** jest natychmiastowy.
- Synchronizacja do Firebase przez **WorkManager**.
- Konflikty: ostatnia modyfikacja (`updatedAt`) wygrywa.
- Dodatkowa strategia: kolejka `pendingSync` z retry.

## 9) Ekrany aplikacji
1. **Home** — lista zakupów + szybkie dodawanie.
2. **History** — historia zakupów i ceny.
3. **Favorites** — najczęściej kupowane produkty.
4. **Stats** — miesięczne i roczne wydatki.
5. **Settings** — konto domowe i synchronizacja.

## 10) Przykładowy flow danych
1. Użytkownik dodaje produkt.
2. ViewModel wywołuje `AddItem` (Domain).
3. Repo zapisuje lokalnie (Room).
4. WorkManager synchronizuje do Firebase w tle.

## 11) Plan integracji z Firebase (kroki)
1. Dodanie `RemoteDataSource` w module `data`.
2. Mapowanie encji Room <-> Firestore.
3. Konfiguracja Auth i modelu Household.
4. Synchronizacja w tle i rozwiązywanie konfliktów.

---

Jeśli chcesz, mogę przygotować **szkielet projektu w Kotlin + Compose** (foldery, klasy, przykładowy UI i baza Room).
