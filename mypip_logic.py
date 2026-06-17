import sys
import os
from datetime import datetime

LOG_FILE = "pip_detailed_history.txt"
TEMP_BEFORE = "temp_before.txt"

def get_installed_packages():
    """Взима текущото състояние на пакетите чрез pip freeze"""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    if result.returncode == 0:
        return [line.strip() for line in result.stdout.split('\n') if line.strip()]
    return []

def main():
    if len(sys.argv) < 2:
        return

    phase = sys.argv[1]          # Взима '0' или '2'
    pip_args = sys.argv[2:]      # Взима параметрите (напр. ['install', 'requests'])
    command = pip_args[0].lower() if pip_args else ""

    # Проверяваме дали командата изобщо е за инсталация или деинсталация
    if command not in ["install", "uninstall"]:
        return

    # --- ФАЗА 1: ПРЕДИ ИЗПЪЛНЕНИЕТО ---
    if phase == "0":
        # 1. Записваме какво иска да направи потребителят
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] ЗАЯВКА: mypip {" ".join(pip_args)}\n")
        
        # 2. Правим снимка ПРЕДИ и я пазим във временния файл
        packages = get_installed_packages()
        with open(TEMP_BEFORE, "w", encoding="utf-8") as f:
            f.write("\n".join(packages))

    # --- ФАЗА 2 (в нашия код белязана като '2'): СЛЕД ИЗПЪЛНЕНИЕТО ---
    elif phase == "2":
        # 1. Прочитаме състоянието ПРЕДИ от временния файл
        if os.path.exists(TEMP_BEFORE):
            with open(TEMP_BEFORE, "r", encoding="utf-8") as f:
                packages_before = set(line.strip() for line in f.readlines() if line.strip())
            os.remove(TEMP_BEFORE) # Изтриваме временния файл, вече не ни трябва
        else:
            packages_before = set()

        # 2. Правим снимка СЛЕД директно в паметта
        packages_after = set(get_installed_packages())

        # 3. Сравняваме и записваме резултата в лога
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            if command == "install":
                new_packages = packages_after - packages_before
                if new_packages:
                    f.write("УСПЕШНО ИНСТАЛИРАНИ ПАКЕТИ И ВЕРСИИ:\n")
                    for pkg in sorted(new_packages):
                        f.write(f"  + {pkg}\n")
                else:
                    f.write("ОТЧЕТ: Операцията приключи. Няма добавени нови пакети.\n")
                    
            elif command == "uninstall":
                removed_packages = packages_before - packages_after
                if removed_packages:
                    f.write("УСПЕШНО ДЕИНСТАЛИРАНИ ПАКЕТИ:\n")
                    for pkg in sorted(removed_packages):
                        f.write(f"  - {pkg}\n")
                else:
                    f.write("ОТЧЕТ: Операцията приключи. Няма премахнати пакети.\n")
            
            f.write("\n") # Празен ред за разделител

if __name__ == "__main__":
    main()
