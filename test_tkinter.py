import tkinter as tk

root = tk.Tk()
root.title("Тест Tkinter")

label = tk.Label(root, text="Tkinter установлен успешно!")
label.pack(padx=20, pady=20)

button = tk.Button(root, text="Закрыть", command=root.quit)
button.pack(pady=10)

root.mainloop() 