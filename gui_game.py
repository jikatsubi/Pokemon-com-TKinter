import tkinter as tk
from tkinter import ttk, messagebox
import random
from pokemon  import POKEDEX, Move

def tiebreak():
    return random.random()

def cpu_choose_move(pkm):
    usable = [m for m in pkm.moves if m.can_use()]
    if not usable:
        return None
    return random.choice(usable)

class HPBar(ttk.Frame):
    def __init__(self, master, label, width=220, height=18):
        super().__init__(master)
        self.width = width
        self.height = height
        self.lbl = ttk.Label(self, text=label, font=("Segoe UI", 10, "bold"))
        self.lbl.pack(anchor="w")
        self.canvas = tk.Canvas(self, width=width, height=height, highlightthickness=0, bg="#f0f0f0")
        self.canvas.pack(fill="x", expand=True)
        self.text = self.canvas.create_text(width//2, height//2, text="", font=("Segoe UI", 9))
        self.rect_bg = self.canvas.create_rectangle(0, 0, width, height, fill="#ddd", outline="")
        self.rect_hp = self.canvas.create_rectangle(0, 0, width, height, fill="#55c252", outline="")

    def set(self, current, maximum, name=None, ptype=None):
        ratio = 0 if maximum == 0 else max(0, min(1, current/maximum))
        fill_w = int(self.width * ratio)
        self.canvas.coords(self.rect_hp, 0, 0, fill_w, self.height)
        if ratio > 0.5:
            color = "#55c252"
        elif ratio > 0.2:
            color = "#d3bb2f"
        else:
            color = "#cf4949"
        self.canvas.itemconfig(self.rect_hp, fill=color)
        label = f"{name or ''} [{ptype or ''}]  HP: {current}/{maximum}"
        self.canvas.itemconfig(self.text, text=label)

class BattleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mini Pokémon OOP - Tkinter")
        self.geometry("880x560")
        self.minsize(820, 520)

        self.player = None
        self.cpu = None
        self.turn = 1
        self.battle_started = False

        self._build_layout()

    def _build_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self, padding=10)
        top.grid(row=0, column=0, sticky="ew")
        sel_frame = ttk.LabelFrame(top, text="Escolha seus Pokémon")
        sel_frame.pack(fill="x")

        self.poke_names = list(POKEDEX.keys())
        self.var_player = tk.StringVar(value=self.poke_names[0])
        self.var_cpu = tk.StringVar(value=random.choice(self.poke_names))

        ttk.Label(sel_frame, text="Você:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.cmb_player = ttk.Combobox(sel_frame, textvariable=self.var_player, values=self.poke_names, state="readonly", width=16)
        self.cmb_player.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(sel_frame, text="Rival (CPU):").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.cmb_cpu = ttk.Combobox(sel_frame, textvariable=self.var_cpu, values=self.poke_names, state="readonly", width=16)
        self.cmb_cpu.grid(row=0, column=3, padx=6, pady=6, sticky="w")

        self.btn_start = ttk.Button(sel_frame, text="Iniciar Batalha", command=self.start_battle)
        self.btn_start.grid(row=0, column=4, padx=10, pady=6)

        self.btn_reset = ttk.Button(sel_frame, text="Novo Sorteio", command=self.randomize_cpu)
        self.btn_reset.grid(row=0, column=5, padx=4, pady=6)

        main = ttk.Frame(self, padding=8)
        main.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        arena = ttk.Frame(main)
        arena.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        arena.columnconfigure(0, weight=1)
        arena.rowconfigure(2, weight=1)

        self.bar_player = HPBar(arena, "Seu Pokémon")
        self.bar_player.grid(row=0, column=0, sticky="ew", pady=(0,6))

        self.bar_cpu = HPBar(arena, "Pokémon do Rival")
        self.bar_cpu.grid(row=1, column=0, sticky="ew", pady=(0,6))

        log_frame = ttk.LabelFrame(arena, text="Log da Batalha")
        log_frame.grid(row=2, column=0, sticky="nsew")
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.txt_log = tk.Text(log_frame, wrap="word", height=14, state="disabled")
        self.txt_log.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(log_frame, command=self.txt_log.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.txt_log.configure(yscrollcommand=scroll.set)

        side = ttk.LabelFrame(main, text="Seus Golpes")
        side.grid(row=0, column=1, sticky="nsew")
        for i in range(4):
            side.rowconfigure(i, weight=1)
        side.columnconfigure(0, weight=1)

        self.move_buttons = []
        for i in range(4):
            btn = ttk.Button(side, text=f"-", command=lambda i=i: self.on_move_click(i), state="disabled")
            btn.grid(row=i, column=0, sticky="ew", padx=8, pady=8, ipady=8)
            self.move_buttons.append(btn)

        self.lbl_turn = ttk.Label(side, text="Turno: -", anchor="center", font=("Segoe UI", 10, "bold"))
        self.lbl_turn.grid(row=4, column=0, sticky="ew", padx=8, pady=8)

        tip = "Dica: golpes com o mesmo tipo do seu Pokémon recebem STAB (1.5x)."
        self.lbl_tip = ttk.Label(side, text=tip, wraplength=250, foreground="#555")
        self.lbl_tip.grid(row=5, column=0, sticky="ew", padx=8, pady=(0,8))

    def randomize_cpu(self):
        self.var_cpu.set(random.choice(self.poke_names))

    def start_battle(self):
        if self.battle_started:
            if not messagebox.askyesno("Reiniciar", "Reiniciar a batalha? O progresso atual será perdido."):
                return
        p_cls = POKEDEX[self.var_player.get()]
        c_cls = POKEDEX[self.var_cpu.get()]
        self.player = p_cls(self.var_player.get())
        self.cpu = c_cls(self.var_cpu.get())
        self.turn = 1
        self.battle_started = True
        self._refresh_ui(full=True)
        self._log(f"=== BATALHA INICIADA ===")
        self._log(f"Você escolheu {self.player.name}. O rival escolheu {self.cpu.name}.")
        self._update_move_buttons(True)

    def _refresh_ui(self, full=False):
        if self.player:
            self.bar_player.set(self.player.hp, self.player.max_hp, self.player.name, self.player.type)
            for i, btn in enumerate(self.move_buttons):
                if i < len(self.player.moves):
                    mv = self.player.moves[i]
                    btn.configure(text=f"{i+1}. {mv.name} [{mv.type}]  Pwr {mv.power}  PP {mv.pp}/{mv.max_pp}")
                else:
                    btn.configure(text="-", state="disabled")
        if self.cpu:
            self.bar_cpu.set(self.cpu.hp, self.cpu.max_hp, self.cpu.name, self.cpu.type)
        self.lbl_turn.configure(text=f"Turno: {self.turn}")
        if full:
            self._clear_log()

    def _clear_log(self):
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.configure(state="disabled")

    def _log(self, msg):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def _update_move_buttons(self, enabled):
        state = "normal" if enabled else "disabled"
        for i, btn in enumerate(self.move_buttons):
            if not self.player or i >= len(self.player.moves):
                btn.configure(state="disabled")
                continue
            mv = self.player.moves[i]
            btn.configure(state=state if mv.can_use() else "disabled")

    def on_move_click(self, idx):
        if not self.battle_started or not self.player or not self.cpu:
            return
        if idx >= len(self.player.moves):
            return
        mv = self.player.moves[idx]
        if not mv.can_use():
            messagebox.showinfo("Sem PP", f"Sem PP para {mv.name}.")
            self._update_move_buttons(True)
            return

        self._update_move_buttons(False)

        if self.player.is_fainted() or self.cpu.is_fainted():
            winner = self.cpu.name if self.player.is_fainted() else self.player.name
            self._end_battle(winner=winner)
            return

        order = sorted([self.player, self.cpu], key=lambda x: (x.speed, tiebreak()), reverse=True)

        for attacker in order:
            if attacker.is_fainted():
                continue
                
            defender = self.cpu if attacker is self.player else self.player
            
            if defender.is_fainted():
                continue

            if attacker is self.player:
                move = mv
            else:
                move = cpu_choose_move(attacker)
                if move is None:
                    self._log(f"{attacker.name} está sem PP e não pode agir.")
                    continue

            damage, eff, had_stab = move.use(attacker, defender)
            eff_str = "super efetivo!" if eff > 1 else ("pouco efetivo..." if eff < 1 else "efetividade normal.")
            stab_str = " com STAB" if had_stab else ""
            self._log(f"{attacker.name} usou {move.name}{stab_str}! Causou {damage} de dano ({eff_str})")

            self._refresh_ui()

            if defender.is_fainted():
                self._log(f"{defender.name} desmaiou!")
                self._end_battle(winner=attacker.name)
                return

        self.turn += 1
        self._refresh_ui()
        self._update_move_buttons(True)

    def _end_battle(self, winner):
        self._log(f"=== FIM DA LUTA: {winner} venceu! ===")
        self._update_move_buttons(False)
        self.battle_started = False
        messagebox.showinfo("Fim da Batalha", f"{winner} venceu!")

if __name__ == "__main__":
    app = BattleGUI()
    app.mainloop()