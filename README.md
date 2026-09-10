# KeepAwake

**ПК не засыпает.** Включил — система и экран не уходят в сон. Есть окно и трей.

**Автор:** darkshade ([@vlx0](https://github.com/vlx0))

**365 дней open source** · **неделя 3 — «Окна и рабочий стол»**.

---

## Как пользоваться

1. Запусти `start.bat` / `run_keepawake.pyw`
2. Сразу режим «Не спит»
3. Кнопка в окне или пункт в трее — вкл/выкл
4. Закрытие окна → в трей; **Выход** в трее — выключить программу

## Установка

```powershell
git clone https://github.com/vlx0/KeepAwake.git
cd KeepAwake
python -m pip install -r requirements.txt
pythonw run_keepawake.pyw
```

Или `setup.bat` / `start.bat`.

Нужен Windows 10+ и Python 3.10+.

## Лицензия

MIT. См. [LICENSE](LICENSE).
